from pathlib import Path
from typing import Callable

from inspect_ai._eval.list import task_files as candidate_files
from inspect_ai._util.decorator import parse_decorators

from gage_inspect.patch import patch_task_description

from ._dataset import DatasetInfo

patch_task_description()


def list_datasets(
    globs: str | list[str] | None = None,
    absolute: bool = False,
    root_dir: Path | None = None,
    filter: Callable[[DatasetInfo], bool] | None = None,
) -> list[DatasetInfo]:
    """List the datasets located at the specified locations.

    Args:
        globs (str | list[str]): File location(s). Can be
           globs (e.g. have bash-style wildcards).
        absolute (bool): Return absolute paths (defaults
           to False)
        root_dir (Path): Base directory to scan from
           (defaults to current working directory)
        filter (Callable[[DatasetInfo], bool] | None):
           Filtering function.

    Returns:
        List of DatasetInfo
    """
    # resolve globs
    globs = (
        globs if isinstance(globs, list) else [globs] if isinstance(globs, str) else []
    )
    root_dir = root_dir or Path.cwd()

    # build list of datasets to return
    datasets: list[DatasetInfo] = []
    for file in candidate_files(globs, root_dir):
        datasets.extend(parse_datasets(file, root_dir, absolute))

    # filter if necessary
    if filter:
        datasets = [ds for ds in datasets if filter(ds)]

    # return sorted
    return sorted(datasets, key=lambda d: (d.file, d.name))


def parse_datasets(path: Path, root_dir: Path, absolute: bool) -> list[DatasetInfo]:
    decorators = parse_decorators(path, "dataset")
    return [
        DatasetInfo(
            file=dataset_path(path, root_dir, absolute),
            name=decorator[0],
            attribs=decorator[1],
        )
        for decorator in decorators
    ]


# manage relative vs. absolute paths
def dataset_path(path: Path, root_dir: Path, absolute: bool) -> str:
    if absolute:
        return path.resolve().as_posix()
    else:
        return path.relative_to(root_dir).as_posix()
