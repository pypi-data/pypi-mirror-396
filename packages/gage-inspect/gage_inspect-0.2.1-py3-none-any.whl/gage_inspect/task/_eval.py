import os
import random

from inspect_ai._cli.eval import eval_command


def eval_tasks(
    tasks: list[str],
    models: list[str],
    task_args: list[str] | None = None,
    dataset: str | None = None,
    limit: int | None = None,
    samples: list[str] | None = None,
    shuffle: bool = False,
    sandbox: str | None = None,
    epochs: int | None = None,
    max_tasks: int | None = None,
    log_dir: str | None = None,
):
    args = [*tasks]
    if models:
        args.extend(["--model", ",".join(models)])
    for arg in task_args or []:
        args.extend(["-T", arg])
    if limit is not None:
        args.extend(["--limit", str(limit)])
    if samples:
        args.extend(["--sample-id", ".".join(samples)])
    if shuffle:
        seed = random.randint(0, 1_000_000_000)
        args.extend(["--sample-shuffle", str(seed)])
    if sandbox:
        args.extend(["--sandbox", sandbox])
    if epochs is not None:
        args.extend(["--epochs", str(epochs)])
    if max_tasks is not None:
        args.extend(["--max-tasks", str(max_tasks)])
    args.extend(["--tags", "type:eval"])
    if log_dir:
        args.extend(["--log-dir", log_dir])

    # Dataset config is currently by way of env vars
    if dataset:
        os.environ["EVAL_DATASET"] = dataset

    eval_command(args)
