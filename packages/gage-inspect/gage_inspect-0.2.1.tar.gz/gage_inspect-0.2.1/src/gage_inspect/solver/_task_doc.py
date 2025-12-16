import yaml
from inspect_ai import Task
from inspect_ai.solver import Generate, Solver, TaskState, solver

from gage_inspect.patch import patch_active_task, patch_task_description
from gage_inspect.task import active_task, parse_task_doc

patch_active_task()
patch_task_description()

PROLOGUE_TEMPLATE = """
Perform this task:

<task_description>
{task_description}
</task_description>
""".strip()

INPUTS_TEMPLATE = """
Here are the task inputs:

<inputs>
{}
</inputs>
""".strip()

OUTPUT_DESCRIPTION_TEMPLATE = """
The output should conform to this description:

<output_description>
{}
</output_description>

Do not explain the results. Do not include inputs or other context. Do
not apply formatting. Return only the generated output value.
""".strip()

INPUT_TEMPLATE = '<{name} description="{description}">{value}</{name}>'


@solver
def task_doc(
    prologue: str | None = None,
    inputs: str | None = None,
    output_description: str | None = None,
) -> Solver:
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        state.user_prompt.content = task_doc_prompt(
            active_task(),
            state.input_text,
            prologue,
            inputs,
            output_description,
        )
        return await generate(state)

    return solve


def task_doc_prompt(
    task: Task,
    input: str,
    prologue: str | None = None,
    inputs: str | None = None,
    output_description: str | None = None,
):
    # Get docstring for active task
    doc = parse_task_doc(task.attribs.get("__doc__") or "")
    if not doc.description:
        raise ValueError("task_doc solver requires a docstring with a description")

    # Prompt starts with the task description
    prompt = [
        resolve(
            prologue or PROLOGUE_TEMPLATE,
            task_description=doc.description.strip(),
        )
    ]

    # Task inputs
    if doc.params:
        # If one param, use input as param value
        if len(doc.params) == 1:
            param = doc.params[0]
            prompt.append(
                resolve(
                    inputs or INPUTS_TEMPLATE,
                    INPUT_TEMPLATE.format(
                        name=param.arg_name,
                        description=param.description or "",
                        value=input,
                    ),
                )
            )
        # Multiple params require parseable YAML/JSON for values
        else:
            try:
                data = yaml.safe_load(input)
            except Exception as e:
                raise ValueError(f"input must be valid YAML/JSON: {e}")
            else:
                if not isinstance(data, dict):
                    raise ValueError("input must be a dict/map of named values")
                prompt.append(
                    resolve(
                        inputs or INPUTS_TEMPLATE,
                        "\n".join(
                            [
                                INPUT_TEMPLATE.format(
                                    name=param.arg_name,
                                    description=param.description or "",
                                    value=data.get(param.arg_name) or "not specified",
                                )
                                for param in doc.params
                            ]
                        ),
                    )
                )
    else:
        prompt.append(resolve(INPUTS_TEMPLATE, input))

    # Expected output
    if output_description or doc.returns:
        prompt.append(
            resolve(
                output_description or OUTPUT_DESCRIPTION_TEMPLATE,
                doc.returns.description if doc.returns else "",
            )
        )

    return "\n\n".join(prompt)


def resolve(template: str, *args, **kw) -> str:
    try:
        return template.format(*args, **kw)
    except (IndexError, KeyError):
        return template
