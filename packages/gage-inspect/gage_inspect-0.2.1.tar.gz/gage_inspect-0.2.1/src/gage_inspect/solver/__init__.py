from gage_inspect.patch import patch_task_dataset

from ._template import input_template
from ._task_doc import task_doc

# Intended side effect of using any solver is to support decoupled
# datasets
patch_task_dataset()

__all__ = [
    "input_template",
    "task_doc",
]
