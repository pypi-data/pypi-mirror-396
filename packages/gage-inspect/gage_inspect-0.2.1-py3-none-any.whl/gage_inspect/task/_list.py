from inspect_ai import TaskInfo
from inspect_ai._eval.list import list_tasks as inspect_list_tasks

from gage_inspect.patch import patch_task_description

patch_task_description()


def list_tasks(path: list[str]) -> list[TaskInfo]:
    return inspect_list_tasks(path)
