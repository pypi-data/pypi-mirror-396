from gage_inspect.patch import patch_task_dataset

from ._match import match
from ._model import llm_judge

# Intended side effect of using any scorer is to support decoupled
# datasets
patch_task_dataset()

__all__ = [
    "llm_judge",
    "match",
]
