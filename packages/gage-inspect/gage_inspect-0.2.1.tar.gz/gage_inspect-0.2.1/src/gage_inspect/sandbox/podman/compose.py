import json
import os
import shlex
from logging import getLogger
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel

from inspect_ai._util.trace import trace_message
from inspect_ai.util._display import display_type, display_type_plain
from inspect_ai.util._subprocess import ExecResult, subprocess

from .service import ComposeService, services_healthcheck_time
from .util import ComposeProject, is_inspect_project

logger = getLogger(__name__)

UP_TIMEOUT = 120
DOWN_TIMEOUT = 60
CP_TIMEOUT = 120
RMI_TIMEOUT = 60
MAX_EXEC_RETRIES = 2


async def compose_up(project: ComposeProject, services: dict[str, ComposeService]):
    cmd = ["up", "--detach"]

    # Use service healthcheck for up timeout if available otherwise use
    # hard-coded value.
    healthcheck_time = services_healthcheck_time(services)
    if healthcheck_time > 0:
        trace_message(logger, "Podman", "Podman services heathcheck timeout: {timeout}")
        cmd.extend(["--timeout", str(healthcheck_time)])
    else:
        cmd.extend(["--timeout", str(UP_TIMEOUT)])

    # Start the environment. Note that we don't check the result because
    # docker will return a non-zero exit code for services that exit
    # (even successfully) when passing the --wait flag (see
    # https://github.com/docker/compose/issues/10596). In practice, we
    # will catch any errors when calling compose_check_running()
    # immediately after we call compose_up().
    return await compose_command(cmd, project=project)


async def compose_down(project: ComposeProject, quiet: bool = True):
    cwd = os.path.dirname(project.config) if project.config else None
    result = await compose_command(
        ["down", "--volumes"],
        project=project,
        timeout=DOWN_TIMEOUT,
        cwd=cwd,
        capture_output=quiet,
        ansi="never",
    )
    try:
        if not result.success:
            raise RuntimeError(
                f"Error stopping container for project '{project.name}'\n\n{result.stderr}"
            )
    finally:
        await delete_project_images(project=project, cwd=cwd)


async def compose_cp(
    src: str,
    dest: str,
    project: ComposeProject,
    cwd: str | Path | None = None,
    output_limit: int | None = None,
):
    result = await compose_command(
        ["cp", "-L", "--", src, dest],
        project=project,
        timeout=CP_TIMEOUT,
        cwd=cwd,
        output_limit=output_limit,
    )
    if not result.success:
        raise RuntimeError(
            f"Failed to copy file from '{src}' to '{dest}': {result.stderr}"
        )


async def check_running(services: list[str], project: ComposeProject):
    """Confirms that the specified list of services are all started.

    Returns items in services that are not running.
    """
    running: list[str] = [
        service["Service"] for service in await compose_ps(project=project)
    ]
    return [name for name in running if name not in services]


Status = Literal[
    "paused",
    "restarting",
    "removing",
    "running",
    "dead",
    "created",
    "exited",
]


async def compose_ps(
    project: ComposeProject,
    status: Status | None = None,
    all: bool = False,
):
    """Returns a list of services.

    By default returns only running services.

    If `all` is True, returns all services matching `status`.
    """
    if not all and not status:
        status = "running"

    # `podman compose ps` doesn't expose ps args - use `--podman-args`
    podman_args = ["--format", "json"]
    if status:
        podman_args.extend(["--filter", f"status={status}"])

    # `--podman-args` options apply to `podman compose` and need to
    # appear before `ps`
    result = await compose_command(
        ["--podman-args", shlex.join(podman_args), "ps"],
        project=project,
        timeout=60,
    )
    if not result.success:
        raise RuntimeError(f"Error querying for running services: {result.stderr}")

    return [apply_name_and_service(service) for service in json.loads(result.stdout)]


def apply_name_and_service(service: dict[str, Any]):
    """Applies the 'Name' and 'Service" items to service.

    Maps Podman service attrs to Docker compatible.

    service['Names'][0] -> 'Name'
    service['Labels']['com.docker.compose.service'] -> 'Service'
    """
    assert "Name" not in service, service
    assert "Service" not in service, service
    try:
        service["Name"] = service["Names"][0]
        service["Service"] = service["Labels"]["com.docker.compose.service"]
    except (KeyError, IndexError) as e:
        raise AssertionError(f"Unexpected service content ({e}): {service}")
    else:
        return service


async def compose_build(project: ComposeProject):
    result = await compose_command(
        ["build"],
        project=project,
        timeout=None,  # no timeout for build
    )
    if not result.success:
        raise RuntimeError(f"Error building container:\n\n{result.stderr}")


async def compose_pull(
    service: str,
    project: ComposeProject,
    capture_output: bool = False,
):
    return await compose_command(
        ["pull", service],
        project=project,
        timeout=None,  # no timeout for pull
        capture_output=capture_output,
    )


async def compose_exec(
    command: list[str],
    *,
    project: ComposeProject,
    timeout: int | None,
    concurrency: bool = True,
    input: str | bytes | None = None,
    output_limit: int | None = None,
):
    return await compose_command(
        ["exec", "-T"] + command,
        project=project,
        timeout=timeout,
        input=input,
        forward_env=False,
        output_limit=output_limit,
        concurrency=concurrency,
    )


async def compose_services(project: ComposeProject):
    result = await compose_command(["config"], project=project, timeout=60)
    if not result.success:
        raise RuntimeError(f"Error reading docker config: {result.stderr}")
    return yaml.safe_load(result.stdout)["services"]


class Project(BaseModel):
    Name: str
    Status: str
    ConfigFiles: str | None


async def compose_ls():
    result = await subprocess(["podman", "compose", "ls", "--all", "--format", "json"])
    if not result.success:
        raise RuntimeError(f"Error getting containers: {result.stderr}")

    return [
        Project(**project)
        for project in json.loads(result.stdout)
        if is_inspect_project(project["Name"])
    ]


async def delete_project_images(project: ComposeProject, *, cwd: str | None = None):
    # Get images for project
    result = await subprocess(["podman", "images", "--format", "json"], cwd=cwd)
    if not result.success:
        raise RuntimeError(f"Error getting images\n\n{result.stderr}")

    for image in json.loads(result.stdout):
        for name in image["Names"]:
            if name.startswith(project.name):
                result = await subprocess(
                    ["podman", "rmi", name],
                    timeout=RMI_TIMEOUT,
                    capture_output=True,
                )
                if not result.success:
                    logger.warning("Error removing image %s: %s", image, result.stderr)


async def compose_command(
    cmd: list[str],
    *,
    project: ComposeProject,
    timeout: int | None = None,
    concurrency: bool = True,
    input: str | bytes | None = None,
    cwd: str | Path | None = None,
    forward_env: bool = True,
    capture_output: bool = True,
    output_limit: int | None = None,
    ansi: Literal["never", "always", "auto"] | None = None,
) -> ExecResult[str]:
    # Args
    args = ["podman", "compose"]
    if not ansi and display_type_plain():
        ansi = "never"
    if ansi == "never":
        args.append("--no-ansi")
    if display_type() == "none":
        args.extend(["--progress", "quiet"])
    args.extend(["--project-name", project.name])
    if project.config:
        args.extend(["-f", project.config])
    args.extend(cmd)

    # Env
    env = project.env if project.env and forward_env else {}

    return await subprocess(
        args,
        input=input,
        cwd=cwd,
        env=env,
        timeout=timeout,
        capture_output=capture_output,
        output_limit=output_limit,
        concurrency=concurrency,
    )
