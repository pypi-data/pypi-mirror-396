from inspect_ai.log import EvalLogInfo, list_eval_logs


def list_logs(log_dir: str, deleted: bool = False) -> list[EvalLogInfo]:
    if deleted:
        return _list_deleted_logs(log_dir)
    return list_eval_logs(log_dir)


def _list_deleted_logs(log_dir: str):
    # Inspect always includes *.eval files, regardless of format
    logs = list_eval_logs(
        log_dir,
        formats=["eval.deleted", "json.deleted"],  # type: ignore
    )
    return [log for log in logs if log.name.endswith(".deleted")]
