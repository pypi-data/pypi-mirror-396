from contextvars import ContextVar

from inspect_ai import Task


def set_active_task(generate: Task) -> None:
    _active_task.set(generate)


def active_task() -> Task:
    return _active_task.get()


_active_task: ContextVar[Task] = ContextVar("_active_task")
