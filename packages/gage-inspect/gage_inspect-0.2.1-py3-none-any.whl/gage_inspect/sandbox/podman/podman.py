import base64
import errno
import json
import os
import shlex
import tempfile
from logging import getLogger
from pathlib import Path
from typing import Literal, NamedTuple, Union, overload

from inspect_ai._util.error import PrerequisiteError
from inspect_ai.util._sandbox.environment import (
    HostMapping,
    PortMapping,
    SandboxConnection,
    SandboxEnvironment,
    SandboxEnvironmentConfigType,
)
from inspect_ai.util._sandbox.limits import (
    SandboxEnvironmentLimits,
    verify_exec_result_size,
    verify_read_file_size,
)
from inspect_ai.util._sandbox.registry import sandboxenv
from inspect_ai.util._subprocess import ExecResult, subprocess
from typing_extensions import override

from .cleanup import (
    cli_cleanup,
    project_cleanup,
    project_cleanup_shutdown,
    project_cleanup_startup,
    project_record_auto_compose,
    project_startup,
)
from .compose import (
    check_running,
    compose_build,
    delete_project_images,
    compose_cp,
    compose_exec,
    compose_pull,
    compose_services,
    compose_up,
    compose_ps,
)
from .config import CONFIG_FILES, DOCKERFILE
from .internal import build_internal_image, is_internal_image
from .prereqs import validate_prereqs
from .util import ComposeProject, task_project_name

logger = getLogger(__name__)

WRITE_FILE_TIMEOUT = 180


@sandboxenv(name="podman")
class PodmanSandboxEnvironment(SandboxEnvironment):
    @classmethod
    def config_files(cls) -> list[str]:
        return CONFIG_FILES + [DOCKERFILE]

    @classmethod
    def default_concurrency(cls) -> int | None:
        count = os.cpu_count() or 1
        return 2 * count

    @classmethod
    async def task_init(
        cls,
        task_name: str,
        config: SandboxEnvironmentConfigType | None,
    ):
        # validate prereqs
        await validate_prereqs()

        # intialize project cleanup
        project_cleanup_startup()

        try:
            # create project
            project = await ComposeProject.create(
                name=task_project_name(task_name), config=config
            )

            # record auto compose
            project_record_auto_compose(project)

            # build containers which are out of date
            await compose_build(project)

            # cleanup images created during build
            await delete_project_images(project)

            services = await compose_services(project)
            for name, service in services.items():
                # if the service has an explicit container_name then
                # error (as this won't work w/ epochs > 1)
                container_name = service.get("container_name", None)
                if container_name:
                    raise PrerequisiteError(
                        f"ERROR: Service '{name}' includes an explicitly configured "
                        f"container_name ('{container_name}'). This is not permitted, "
                        "as container names should be provisioned by Docker compose "
                        "and an explicit container_name will not work with epochs > 1."
                    )

                # build internal images
                image = service.get("image", None)
                if image and is_internal_image(image):
                    await build_internal_image(image)
                # pull any remote images
                elif (
                    service.get("build", None) is None
                    and service.get("x-local", None) is None
                ):
                    # TODO - time-nconsuming even when images are locally
                    # available - any way to speed this up?
                    result = await compose_pull(name, project)
                    if not result.success:
                        image = service.get("image", "(unknown)")
                        logger.error(
                            f"Failed to pull docker image '{image}' from remote registry. "
                            "If this is a locally built image add 'x-local: true' to the "
                            "the service definition to prevent this error."
                        )

            # provide some space above task display
            print()

        except BaseException:
            await project_cleanup_shutdown(True)
            raise

    @override
    @classmethod
    async def task_init_environment(
        cls, config: SandboxEnvironmentConfigType | None, metadata: dict[str, str]
    ) -> dict[str, str]:
        # get interpolated environment variables and underlying config path and text
        resolved = resolve_config_environment(config, metadata)

        # don't even consider sample-specific environment if there are no sample metadata refs
        if not resolved or not resolved.env:
            return {}

        # resolve images using our env vars
        result = await subprocess(
            ["podman", "compose", "-f", resolved.config_file, "config", "--images"],
            env=resolved.env,
        )
        if not result.success:
            raise RuntimeError(
                f"Unexpected error reading compose file '{resolved.config_file}': {result.stderr}"
            )

        # look through the images, if one of them doesn't appear in the the
        # config text then this compose file requires its own sample specific
        # environment for resolution
        images = result.stdout.strip().splitlines()
        for image in images:
            if image not in resolved.config_text:
                return resolved.env

        return {}

    @override
    @classmethod
    async def sample_init(
        cls,
        task_name: str,
        config: SandboxEnvironmentConfigType | None,
        metadata: dict[str, str],
    ) -> dict[str, SandboxEnvironment]:
        # create environment variables for sample metadata
        resolved = resolve_config_environment(config, metadata)
        env = resolved.env if resolved else {}

        # create project
        from inspect_ai.log._samples import sample_active

        sample = sample_active()
        project = await ComposeProject.create(
            name=task_project_name(task_name),
            config=config,
            sample_id=sample.sample.id if sample is not None else None,
            epoch=sample.epoch if sample is not None else None,
            env=env,
        )

        # note that the project is running
        project_startup(project)

        try:
            # enumerate the services that will be created
            services = await compose_services(project)
            if not services:
                raise RuntimeError(f"No services defines in project '{project.config}'")

            # start the services
            result = await compose_up(project, services)
            if not result.success:
                raise RuntimeError(
                    f"Error starting container services: {result.stderr}"
                )

            # check to ensure that the services are running (TODO -
            # check_running is slow here, which is surprising - investigate)
            not_running = await check_running(list(services.keys()), project=project)
            if not_running:
                raise RuntimeError(
                    "The following services could not be started: "
                    f"{', '.join(not_running)}\n\n"
                    f"Compose up stderr: {result.stderr}"
                )

            # create sandbox environments for all services
            default_service = "default"
            environments = {}
            for service, service_info in services.items():
                # update the project w/ the working directory
                working_dir = await container_working_dir(service, project)

                # create the docker sandbox environemnt
                env = PodmanSandboxEnvironment(service, project, working_dir)

                # save reference to default service if requested
                if service_info.get("x-default", False):
                    default_service = service

                # record service => environment
                environments[service] = env

            # move default service to front position in (ordered) dict
            # as per `sample_init` spec
            try:
                default_environment = environments.pop(default_service)
            except KeyError:
                raise RuntimeError(
                    "No 'default' service found in Docker compose file. "
                    + "You should either name a service 'default' or add "
                    + "'x-default: true' to one of your service definitions."
                )
            else:
                return {default_service: default_environment} | environments

        except BaseException:
            await project_cleanup(project, True)
            raise

    @override
    @classmethod
    async def sample_cleanup(
        cls,
        task_name: str,
        config: SandboxEnvironmentConfigType | None,
        environments: dict[str, SandboxEnvironment],
        interrupted: bool,
    ) -> None:
        # if we were interrupted - defer cleanup to ask level (this
        # enables us to show output for the cleanup operation)
        if interrupted:
            return

        # use project from first environment
        project = (
            next(iter(environments.values())).as_type(PodmanSandboxEnvironment)._project
        )
        await project_cleanup(project=project, quiet=True)

    @classmethod
    async def task_cleanup(
        cls, task_name: str, config: SandboxEnvironmentConfigType | None, cleanup: bool
    ) -> None:
        await project_cleanup_shutdown(cleanup)

    @classmethod
    async def cli_cleanup(cls, id: str | None) -> None:
        await cli_cleanup(id)

    def __init__(self, service: str, project: ComposeProject, working_dir: str) -> None:
        super().__init__()
        self._service = service
        self._project = project
        self._working_dir = working_dir

    @override
    async def exec(
        self,
        cmd: list[str],
        input: str | bytes | None = None,
        cwd: str | None = None,
        env: dict[str, str] = {},
        user: str | None = None,
        timeout: int | None = None,
        timeout_retry: bool = True,  # Intentionally unused
        concurrency: bool = True,
    ) -> ExecResult[str]:
        opts = []

        if not cwd:
            cwd = self._working_dir
        elif not os.path.isabs(cwd):
            cwd = os.path.join(self._working_dir, cwd)
        opts.extend(["--workdir", cwd])

        if user:
            opts.extend(["--user", user])

        # Forward environment commands to docker compose exec so they
        # will be available to the bash command
        for key, value in env.items():
            opts.extend(["--env", f"{key}={value}"])

        result = await compose_exec(
            opts + [self._service] + cmd,
            project=self._project,
            timeout=timeout,
            input=input,
            output_limit=SandboxEnvironmentLimits.MAX_EXEC_OUTPUT_SIZE,
            concurrency=concurrency,
        )
        verify_exec_result_size(result)
        if result.returncode == 126 and "permission denied" in result.stdout:
            raise PermissionError(f"Permission denied executing command: {result}")

        return result

    @override
    async def write_file(self, file: str, contents: str | bytes) -> None:
        # resolve relative file paths
        file = self.container_file(file)

        # ensure that the directory exists
        parent = Path(file).parent.as_posix()
        if parent != ".":
            result = await self.exec(["mkdir", "-p", parent])
            if not result.success:
                msg = f"Failed to create container directory {parent}: {result.stderr}"
                raise RuntimeError(msg)

        # write the file
        if isinstance(contents, str):
            input = contents
            cmd = 'tee -- "$0" > /dev/null'
        else:
            input = base64.b64encode(contents).decode("US-ASCII")
            cmd = 'base64 -d | tee -- "$0" > /dev/null'
        args = ["sh", "-e", "-c", cmd, file]

        result = await self.exec(args, input, timeout=WRITE_FILE_TIMEOUT)

        if not result.success:
            stderr = result.stderr.lower()
            if "permission denied" in stderr:
                raise PermissionError(result.stderr)
            if "cannot overwrite directory" in stderr or "is a directory" in stderr:
                raise IsADirectoryError(file)
            raise RuntimeError(f"Error creating file {file}\n\n{result.stderr}")

    @overload
    async def read_file(self, file: str, text: Literal[True] = True) -> str: ...

    @overload
    async def read_file(self, file: str, text: Literal[False]) -> bytes: ...

    @override
    async def read_file(self, file: str, text: bool = True) -> Union[str, bytes]:
        # Write the contents to a temp file
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
            # resolve relative file paths
            original_file = file
            file = self.container_file(file)

            # copy the file
            dest_file = os.path.join(temp_dir, os.path.basename(file))
            try:
                await compose_cp(
                    src=f"{self._service}:{file}",
                    dest=os.path.basename(dest_file),
                    project=self._project,
                    cwd=os.path.dirname(dest_file),
                    output_limit=SandboxEnvironmentLimits.MAX_READ_FILE_SIZE,
                )
            except RuntimeError as ex:
                # extract the message and normalise case
                message = str(ex).lower()

                # FileNotFoundError
                if "could not find the file" in message:
                    raise FileNotFoundError(
                        errno.ENOENT, "No such file or directory.", original_file
                    )

                # PermissionError
                elif "permission denied" in message:
                    raise PermissionError(
                        errno.EACCES, "Permission denied.", original_file
                    )
                else:
                    raise ex

            verify_read_file_size(dest_file)

            # read and return w/ appropriate encoding
            if text:
                with open(dest_file, "r", newline="", encoding="utf-8") as f:
                    return f.read()
            else:
                with open(dest_file, "rb") as f:
                    return f.read()

    @override
    async def connection(self, *, user: str | None = None) -> SandboxConnection:
        # find container for service
        services = await compose_ps(project=self._project)
        container = next(
            (
                service["Name"]
                for service in services
                if service["Service"] == self._service
            ),
            None,
        )

        if not container:
            raise ConnectionError(
                f"Service '{self._service} is not currently running.'"
            )

        # vscode doesn't support attaching to a container as a specific user,
        # so don't include the vscode command if a user is specified
        vscode_command = (
            [
                "remote-containers.attachToRunningContainer",
                container,
            ]
            if user is None
            else None
        )

        # return container connection
        return SandboxConnection(
            type="podman",
            command=shlex.join(
                [
                    "podman",
                    "exec",
                    "-it",
                    *(["--user", user] if user else []),
                    container,
                    "bash",
                    "-l",
                ]
            ),
            vscode_command=vscode_command,
            ports=await get_ports_info(container),
            container=container,
        )

    def default_polling_interval(self) -> float:
        return 0.2

    def container_file(self, file: str) -> str:
        path = Path(file)
        if not path.is_absolute():
            path = Path(self._working_dir) / path
        return path.as_posix()


async def container_working_dir(
    service: str, project: ComposeProject, default: str = "/"
) -> str:
    result = await compose_exec(
        [service, "sh", "-c", "pwd"], timeout=60, project=project
    )
    if result.success:
        return result.stdout.strip()
    else:
        logger.warning(
            f"Failed to get working directory for docker container '{service}': "
            + f"{result.stderr}"
        )
        return default


async def get_ports_info(container: str) -> list[PortMapping] | None:
    try:
        result = await subprocess(
            [
                "podman",
                "inspect",
                container,
                "--format",
                "{{json .NetworkSettings.Ports}}",
            ],
            timeout=60,
        )

        if not result.success:
            raise RuntimeError(result.stderr)

        return parse_docker_inspect_ports(result.stdout)

    # It's currently a policy decision to let docker timeouts to be silent.
    except TimeoutError:
        return None


def parse_docker_inspect_ports(json_str: str) -> list[PortMapping] | None:
    """
    Parses the JSON output from `docker inspect {container_name} --format='{{json .NetworkSettings.Ports}}'` to extract port mappings.

    Args:
        json_str (str): A JSON string representing the `NetworkSettings.Ports` output of `docker inspect`. e.g.
          ```
          {
              "5900/tcp": [{"HostIp": "0.0.0.0", "HostPort": "54023"}],
              "8080/tcp": [{"HostIp": "0.0.0.0", "HostPort": "54024"}]
          }
          ```

    Returns:
        list[PortMapping] | None: A list of PortMapping objects if any port mappings are found,
                                   otherwise None.
    """
    data = json.loads(json_str)
    port_mappings = []
    for port_protocol, mappings in data.items():
        if mappings is None:
            continue
        container_port, protocol = port_protocol.split("/")
        host_mappings = [
            HostMapping(host_ip=mapping["HostIp"], host_port=int(mapping["HostPort"]))
            for mapping in mappings
        ]
        port_mapping = PortMapping(
            container_port=int(container_port),
            protocol=protocol,
            mappings=host_mappings,
        )
        port_mappings.append(port_mapping)
    return port_mappings if port_mappings else None


class ConfigEnvironment(NamedTuple):
    config_file: str
    config_text: str
    env: dict[str, str]


def resolve_config_environment(
    config: SandboxEnvironmentConfigType | None,
    metadata: dict[str, str],
) -> ConfigEnvironment | None:
    # create environment variables for sample metadata
    if isinstance(config, str) and Path(config).exists():
        # read the config file
        config_file = config
        with open(config, "r") as f:
            config_text = f.read()

        # only add metadata files if the key is in the file
        env: dict[str, str] = {}
        for key, value in metadata.items():
            key = f"SAMPLE_METADATA_{key.replace(' ', '_').upper()}"
            if key in config_text:
                env[key] = str(value)

        # return resolved
        return ConfigEnvironment(config_file, config_text, env)
    else:
        return None
