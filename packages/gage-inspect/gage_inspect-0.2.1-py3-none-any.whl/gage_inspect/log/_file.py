from pathlib import Path
from typing import Literal

from inspect_ai.log import EvalLog, EvalLogInfo, read_eval_log as inspect_read_eval_log

from gage_inspect.patch import patch_recorder_types

patch_recorder_types()


def read_eval_log(
    log_file: str | Path | EvalLogInfo,
    header_only: bool = False,
    resolve_attachments: bool = False,
    format: Literal["eval", "json", "auto"] = "auto",
) -> EvalLog:
    return inspect_read_eval_log(log_file, header_only, resolve_attachments, format)
