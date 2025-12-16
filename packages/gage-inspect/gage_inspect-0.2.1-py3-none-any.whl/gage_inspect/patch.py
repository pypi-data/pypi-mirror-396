import ast
import importlib.util
import inspect
import os
import re
from typing import Any, Literal

# Limit imports from inspect_ai to types
from inspect_ai import Task
from inspect_ai._eval.registry import TaskType
from inspect_ai._eval.task.run import TaskRunOptions
from inspect_ai.dataset import Dataset, Sample
from inspect_ai.log import EvalLog

# Avoid gage_inspect imports - this module is used by other modules for
# patching and can introduce import cycles


def patch_active_task():
    """Patches task run to set active task.

    When a task is run, it's set using `set_active_task()`. The active
    task can be read using `get_activet_task()`.
    """
    from inspect_ai._eval import run as eval_run_mod
    from inspect_ai._eval.task import run as task_run_mod

    from gage_inspect.task._active import set_active_task

    task_run = task_run_mod.__dict__["task_run"]
    if task_run.__name__ == "patched_task_run":
        return

    async def patched_task_run(options: TaskRunOptions) -> EvalLog:
        set_active_task(options.task)
        return await task_run(options)

    task_run_mod.__dict__["task_run"] = patched_task_run
    eval_run_mod.__dict__["task_run"] = patched_task_run


def patch_task_description():
    """Patches task registration to set task description.

    If `info` doesn't have a descriptioin attribute and the task type
    function has a docstring, the docstring is used to set the task
    description.
    """
    patch_task_description_task_register()
    patch_description_parse_decorator()


def patch_task_description_task_register():
    """Patch task registration to set description from docstring.

    Patches `task_register` in the registry module to set the
    description attrib using the task docstring short description if the
    attrib doesn't already exist.
    """
    from inspect_ai._eval import registry as registry_mod

    from gage_inspect._util import docstring_short_description

    task_register = registry_mod.__dict__["task_register"]
    if task_register.__name__ == "patched_task_register":
        return

    def patched_task_register(
        task: TaskType,
        name: str,
        attribs: dict[str, Any],
        params: list[str],
    ) -> TaskType:
        doc = task.__doc__
        if doc:
            attribs["__doc__"] = doc
        if not attribs.get("description") and doc:
            attribs["description"] = docstring_short_description(doc)
        return task_register(task, name, attribs, params)

    registry_mod.__dict__["task_register"] = patched_task_register


def patch_description_parse_decorator():
    """Patch decorator parser to set description from docstring.

    Patches `parse_decorator` function in the decorator module to set
    the description attrib using the first line of the function
    docstring if description isn't already specified.

    Used for routines that parse the Python source to load decorator
    info for a function.
    """
    from inspect_ai._util import decorator as decorator_mod

    from gage_inspect._util import docstring_short_description

    parse_decorator = decorator_mod.__dict__["parse_decorator"]
    if parse_decorator.__name__ == "patched_parse_decorator":
        return

    def patched_parse_decorator(
        node: ast.FunctionDef, decorator: ast.expr, decorator_name: str
    ) -> tuple[str, dict[str, Any]] | None:
        result = parse_decorator(node, decorator, decorator_name)
        if result is None:
            return None
        name, attribs = result
        doc = ast.get_docstring(node)
        if doc:
            attribs["__doc__"] = doc
        if not attribs.get("description") and doc:
            attribs["description"] = docstring_short_description(doc)
        return name, attribs

    decorator_mod.__dict__["parse_decorator"] = patched_parse_decorator


def patch_task_dataset():
    """Patch Inspect for task dataset support.

    Patches `task_create` to set in the Inspect task loader to assign a
    dataset of one is not already set for a task.

    This allows tasks to be defined independently of a dataset, which is
    suited for building a task for inference and evals, rather than for
    evals exclusively.

    The assignment of a dataset does not affect task run or serve
    operations as samples are derived from user input (e.g. per request).
    """
    from inspect_ai._eval import loader as loader_mod

    task_create = loader_mod.__dict__["task_create"]
    if task_create.__name__ == "patched_task_create":
        return

    def patched_task_create(name: str, **kwargs: Any) -> Task:
        task: Task = task_create(name, **kwargs)
        if not task_has_dataset(task):
            # Assert that we're called by create_file_tasks
            call_stack = inspect.stack()
            assert call_stack[1].function == "create_file_tasks", (
                "unexpected parent call",
                call_stack[1].function,
                call_stack,
            )

            # Get `file` arg in parent call - used to match candidate
            # datasets
            task_file_arg = inspect.stack()[1].frame.f_locals["file"]

            # create_file_tasks changes cwd to task parent - task file
            # is the file arg stripped of it's parent dir
            task_file = os.path.basename(task_file_arg)

            # If we're not being called from `run_task`, try to find a
            # dataset for the task based on task name and file (run task
            # is a different case, where a single sample is created from
            # task input - we don't want to load a dataset)
            if not in_run_call(call_stack):
                dataset = find_task_dataset(task.name, task_file)
                if dataset:
                    task.dataset = dataset
        return task

    loader_mod.__dict__["task_create"] = patched_task_create


def in_run_call(call_stack: list[inspect.FrameInfo]) -> bool:
    for frame in call_stack:
        if frame.function == "run_task_async":
            return True
    return False


def task_has_dataset(task: Task) -> bool:
    return len(task.dataset) != 1 or task.dataset[0] != Sample("prompt")


def find_task_dataset(task_name: str, task_file: str) -> Dataset | None:
    from inspect_ai._util.registry import registry_create

    # Required here to avoid import cycle
    from gage_inspect.dataset import list_datasets

    # List available datasets (local file system scan of parsed ASTs)
    datasets = list_datasets()

    # If EVAL_DATASET var specified, try to find a match
    ds_name_env = os.getenv("EVAL_DATASET")
    if ds_name_env:
        candidates = [ds for ds in datasets if ds.name == ds_name_env]
        if not candidates:
            raise ValueError(f"Unknown dataset '{ds_name_env}'")

    # Otherwise create a sorted list of candidates ordered by task name
    # match, file name match, and default flag. Dataset name sort order
    # is used to break ties.
    else:
        candidates = [
            ds_info
            for (name_match, file_match, _default, ds_info) in sorted(
                [
                    (
                        ds_info.attribs.get("task") == task_name,
                        ds_info.file == task_file,
                        ds_info.attribs.get("default"),
                        ds_info,
                    )
                    for ds_info in datasets
                ],
                key=lambda item: (not item[0], not item[1], not item[2], item[3].name),
            )
            if name_match or file_match
        ]

    if candidates:
        # Use the first (highest priority) candidate
        ds_info = candidates[0]

        # If dataset is defined in a different file, need to load file
        # as module to register dataset
        if ds_info.file != task_file:
            # Load module spec - module name `__dataset_src__` is arbitrary
            spec = importlib.util.spec_from_file_location(
                "__dataset_src__", ds_info.file
            )
            assert spec
            assert spec.loader
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

        # Use registry to create dataset instance
        ds: Dataset = registry_create("dataset", ds_info.name)  # type: ignore

        # Dataset is a read-only ABC that doesn't provide an interface
        # for setting its name property. MemoryDataset uses the
        # attribute `_name` so we work with that.
        if not ds.__dict__.get("_name"):
            ds.__dict__["_name"] = ds_info.name  # type: ignore

        return ds

    return None


def patch_recorder_types():
    """Patch Inspect recorder types to support reads from `*.deleted` logs."""

    from inspect_ai.log._recorders import create as created_mod
    from inspect_ai.log._recorders.eval import EvalRecorder

    if "eval.deleted" in created_mod._recorders:
        return

    class PatchedEvalRecorder(EvalRecorder):
        @classmethod
        def handles_location(cls, location: str) -> bool:
            return location.endswith(".eval") or location.endswith(".eval.deleted")

    created_mod._recorders["eval"] = PatchedEvalRecorder


def patch_scorers():
    """Patch Inspect match scorer to fix numeric processing."""
    from inspect_ai.scorer import _match as match_mod

    match_str = match_mod.__dict__["match_str"]
    if match_str.__name__ == "patched_match_str":
        return

    def try_number(s: str):
        m = re.match(r"(?:['\"\*]*)((?:-)?\d+(?:\.\d+)?)(?:['\"\*]*)", s)
        if not m:
            return None
        s = m.group(1)
        try:
            return int(s)
        except ValueError:
            try:
                return float(s)
            except ValueError:
                return None

    def patched_match_str(
        value: str,
        target: str,
        location: Literal["begin", "end", "any", "exact"] = "end",
        ignore_case: bool = True,
        ignore_punctuation: bool = True,
        numeric: bool = False,
    ):
        if not numeric:
            return match_str(
                value, target, location, ignore_case, ignore_punctuation, numeric
            )
        # Apply different handling for numeric - parse numbers in value
        # and then apply location
        value = value.strip()
        target = target.strip()
        target_num = try_number(target)
        if target_num is None:
            return value, False
        tokens = re.split(r"\s+", value)
        if not tokens:
            return value, False
        if location == "begin":
            return value, try_number(tokens[0]) == target_num
        elif location == "end":
            return value, try_number(tokens[-1]) == target_num
        elif location == "any":
            return value, target_num in [
                n for n in [try_number(s) for s in tokens] if n is not None
            ]
        else:
            assert location == "exact", location
            return value, len(tokens) == 1 and try_number(tokens[0]) == target_num

    match_mod.__dict__["match_str"] = patched_match_str


__all__ = [
    "patch_active_task",
    "patch_task_description",
    "patch_task_description_task_register",
    "patch_recorder_types",
    "patch_scorers",
]
