import os
from typing import Any

from inspect_ai import Task
from inspect_ai._eval.loader import load_tasks
from inspect_ai._eval.task.log import TaskLogger
from inspect_ai._eval.task.util import task_file
from inspect_ai.log import EvalConfig
from inspect_ai.log._recorders.eval import EvalRecorder
from inspect_ai.model import Model, get_model
from shortuuid import uuid


def resolve_task(task: str | Task, task_args: dict[str, Any]):
    if isinstance(task, Task):
        return task
    tasks = load_tasks([task], task_args)
    if not tasks:
        raise ValueError(f"No tasks match '{task}'")
    if len(tasks) > 1:
        matched = ", ".join([task.name for task in tasks])
        raise ValueError(f"Multiple tasks match '{task}': {matched}")
    return tasks[0]


def resolve_model(model: str | Model | None):
    if isinstance(model, Model):
        return model
    return _args_model(model) or _env_model()


def _args_model(model_arg: str | None) -> Model | None:
    if not model_arg:
        return None
    return get_model(model_arg)


def _env_model() -> Model | None:
    model_name = os.getenv("GAGE_MODEL") or os.getenv("INSPECT_EVAL_MODEL")
    if not model_name:
        return None
    return get_model(model_name)


def default_log_dir():
    return os.getenv("INSPECT_LOG_DIR") or "logs"


def init_logger(
    task: Task,
    task_args: dict[str, Any],
    model: Model,
    tags: list[str] | None,
    log_dir: str,
):
    task_id = uuid()
    run_id = uuid()
    recorder = EvalRecorder(log_dir)

    return TaskLogger(
        task_name=task.name,
        task_version=task.version,
        task_file=task_file(task, relative=True),
        task_registry_name=task.registry_name,
        task_display_name=task.display_name,
        task_id=task_id,
        eval_set_id=None,  # TODO eval_set_id,
        run_id=run_id,
        solver=None,  # TODO eval_solver_spec,
        tags=tags,
        model=model,
        model_roles=None,  # TODO resolved_task.model_roles,
        dataset=task.dataset,
        scorer=None,  # TODO ??? eval_scorer_specs,
        metrics=None,  # TODO eval_metrics,
        sandbox=task.sandbox,
        task_attribs=task.attribs,
        task_args=task_args,
        task_args_passed=task_args,
        model_args={},  # TODO resolved_task.model.model_args,
        eval_config=EvalConfig(log_realtime=False),  # TODO task_eval_config,
        metadata=task.metadata,
        recorder=recorder,
        header_only=False,  # TODO header_only,
    )
