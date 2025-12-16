import json
from logging import getLogger
from typing import Callable

import semver
from pydantic import BaseModel

from inspect_ai._util.error import PrerequisiteError
from inspect_ai.util._subprocess import subprocess

logger = getLogger(__name__)


class PodmanClientVersion(BaseModel):
    Version: str
    APIVersion: str


class PodmanVersion(BaseModel):
    Client: PodmanClientVersion


class PodmanComposeVersion(BaseModel):
    version: str


async def validate_prereqs() -> None:
    await validate_podman()
    await validate_podman_compose()


PODMAN_REQUIRED_VERSION = "4.9.3"


async def validate_podman(version: str = PODMAN_REQUIRED_VERSION) -> None:
    def parse_version(stdout: str) -> semver.Version:
        version = PodmanVersion(**json.loads(stdout)).Client.Version
        return semver.Version.parse(version)

    await validate_version(
        cmd=["podman", "version", "--format", "json"],
        parse_fn=parse_version,
        required_version=version,
        feature="Podman",
    )


PODMAN_COMPOSE_REQUIRED_VERSION = "1.0.6"


async def validate_podman_compose(
    version: str = PODMAN_COMPOSE_REQUIRED_VERSION,
) -> None:
    def parse_version(stdout: str) -> semver.Version:
        version = PodmanComposeVersion(**json.loads(stdout)).version
        return semver.Version.parse(version)

    # TODO docker-compose is fine too - require one or the other
    await validate_version(
        cmd=["podman-compose", "version", "--format", "json"],
        parse_fn=parse_version,
        required_version=version,
        feature="podman-compose",
    )


async def validate_version(
    cmd: list[str],
    parse_fn: Callable[[str], semver.Version],
    required_version: str,
    feature: str,
) -> None:
    try:
        result = await subprocess(cmd)
    except FileNotFoundError:
        raise PrerequisiteError(
            "ERROR: Podman sandbox environments require Podman\n\n"
            "Install: https://podman.io/docs/installation"
        )
    else:
        if not result.success:
            raise PrerequisiteError(f"Error getting Podman version: {result.stderr}")
        version = parse_fn(result.stdout)
        if version.compare(required_version) < 0:
            raise PrerequisiteError(
                f"ERROR: Podman sandbox environments require {feature} >= "
                f"{required_version} (current: {version})\n\n"
                "Upgrade:https://podman.io/docs/installation"
            )
