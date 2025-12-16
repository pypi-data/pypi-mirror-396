import inspect
from functools import wraps
import json
from pathlib import Path
from typing import Any, cast

from inspect_ai._util.package import get_installed_package_name
from inspect_ai._util.registry import (
    RegistryInfo,
    extract_named_params,
    registry_add,
    registry_name,
    registry_tag,
)
from inspect_ai.dataset import Dataset, MemoryDataset, Sample

from gage_inspect.patch import patch_task_dataset

from ._dataset import DatasetType, ImpliedDataset

patch_task_dataset()

DATASET_FILE_ATTR = "__dataset_file__"
DATASET_RUN_DIR_ATTR = "__dataset_run_dir__"
DATASET_ALL_PARAMS_ATTR = "__dataset_all_params__"


def dataset(*args: Any, name: str | None = None, **attribs: Any) -> Any:
    r"""Decorator for registering datasets.

    Args:
      *args: Function returning `Dataset`
      name (str | None):
        Optional name for the dataset. Function name is used
        by default.
      **attribs: (dict[str,Any]): Additional dataset attributes.

    Returns:
        Decorated function.
    """

    def wrapper(dataset_type: DatasetType) -> DatasetType:
        # Get the name and parameters of the dataset
        dataset_name = registry_name(
            dataset_type, name or getattr(dataset_type, "__name__")
        )
        params = list(inspect.signature(dataset_type).parameters.keys())

        # Use function docstring for description if not specified in attribs
        if "description" not in attribs:
            if dataset_type.__doc__:
                from gage_inspect._util import docstring_short_description

                attribs["description"] = docstring_short_description(
                    dataset_type.__doc__
                )

        # Create and return the wrapper function
        @wraps(dataset_type)
        def wrapper(*w_args: Any, **w_kwargs: Any) -> Dataset:
            # Create the dataset
            dataset = resolve_implied_dataset(dataset_type(*w_args, **w_kwargs))

            # Tag the dataset with registry information
            registry_tag(
                dataset_type,
                dataset,
                RegistryInfo.model_construct(
                    type="dataset",
                    name=dataset_name,
                    metadata=dict(attribs=attribs, params=params),
                ),
                *w_args,
                **w_kwargs,
            )

            # extract all dataset parameters including defaults
            named_params = extract_named_params(dataset_type, True, *w_args, **w_kwargs)
            setattr(dataset, DATASET_ALL_PARAMS_ATTR, named_params)

            # if its not from an installed package then it is a "local"
            # module import, so set its dataset file and run dir
            if get_installed_package_name(dataset_type) is None:
                module = inspect.getmodule(dataset_type)
                if module and hasattr(module, "__file__") and module.__file__:
                    file = Path(getattr(module, "__file__"))
                    setattr(dataset, DATASET_FILE_ATTR, file.as_posix())
                    setattr(dataset, DATASET_RUN_DIR_ATTR, file.parent.as_posix())

            return dataset

        # functools.wraps overrides the return type annotation of the inner function, so
        # we explicitly set it again
        wrapper.__annotations__["return"] = Dataset

        # Register the dataset type
        return dataset_register(
            dataset=cast(DatasetType, wrapper),
            name=dataset_name,
            attribs=attribs,
            params=params,
        )

    if args:
        # The decorator was used without arguments: @dataset
        func = args[0]
        return wrapper(func)
    else:
        # The decorator was used with arguments: @dataset(name="foo")
        def decorator(func: DatasetType) -> DatasetType:
            return wrapper(func)

        return decorator


def resolve_implied_dataset(val: Dataset | ImpliedDataset) -> Dataset:
    if isinstance(val, Dataset):
        return val

    def sample(item: Sample | str | dict[str, Any]):
        if isinstance(item, Sample):
            return item
        elif isinstance(item, dict):
            attrs = dict(item)
            target = attrs.pop("target", None)
            return Sample(json.dumps(attrs), target=str(target))
        else:
            return Sample(item)

    return MemoryDataset([sample(item) for item in val])


def dataset_register(
    dataset: DatasetType, name: str, attribs: dict[str, Any], params: list[str]
) -> DatasetType:
    r"""Register a dataset.

    Args:
        dataset (DatasetType):
            function that returns a Dataset
        name (str): Name of dataset
        attribs (dict[str,Any]): Attributes of dataset decorator
        params (list[str]): Dataeset parameter names

    Returns:
        Dataset type with registry attributes.
    """
    registry_add(
        dataset,
        RegistryInfo.model_construct(
            type="dataset",
            name=name,
            metadata=dict(attribs=attribs, params=params),
        ),
    )
    return dataset
