import inspect
import string
from typing import Any, Literal, Mapping, Sequence

import yaml
from inspect_ai.solver import Generate, Solver, TaskState, solver
from inspect_ai.util import resource
from pydantic import BaseModel, TypeAdapter

Schema = type | BaseModel | Literal["auto"]


class Template:
    def __init__(self, s):
        self._parsed = list(string.Formatter().parse(s))

    def render(self, vars: dict[str, Any] | None = None):
        vars = vars or {}
        parts = []

        for literal_text, field_name, format_spec, conversion in self._parsed:
            # output the literal text
            if literal_text:
                parts.append(literal_text)

            if field_name is None:
                continue

            if field_name == "":
                field_name = "input"

            # Support nested vars via dot delimiters
            names = field_name.split(".")
            cur = vars
            for name in names:
                try:
                    val = cur[name]
                except KeyError:
                    break
                else:
                    if isinstance(val, Mapping):
                        cur = val
                    else:
                        parts.append(str(val))
                        break

        return "".join(parts)

    def field_names(self):
        # Remove duplicates and coerce "" to "input"
        names: set[str] = set()
        for _, name, _, _ in self._parsed:
            if name is not None:
                names.add(name or "input")
        return names


@solver
def input_template(
    template: str = "{}",
    schema: Schema = "auto",
    params: dict[str, Any] | None = None,
) -> Solver:
    """Set the user message using a template.

    `template` may contain variable references to the sample input.
    Sample input is first processed according to `schema`. The variables
    available to the template are as follows:

    - If `schema` is "auto" (default), input is first processed as
      YAML/JSON. If input can be parsed as valid YAML/JSON, its values
      are made available to the template based on the processed input
      data type. If the input is a dict/map, variables are the dict item
      keys. If it's a list/array, variables are the zero-based indices
      of each list item. All other types are available as the variable
      `input`.

    - If `schema` is a Pydantic base model, the model is used to parse
      and validate the sample input. The validated model fields are made
      available as template variables.

    - If `schema` is a Python type, the type is used to parse and
      validate sample input. The validated value is made available to
      the template using the rules used for "auto" (see above)

    `params` are included as additional template variables. Processed
    template variables take precedence over `params`. For example, if
    the variable `color` appears in both `params` and the processed
    input, the value from the input is used.

    Args:
      template: Template for the user message with variable references
      params: Params used by a message template.

    Returns:
      A solver that sets the user message using the template resolved
      with input variables.
    """
    parsed = Template(resource(template))

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        vars = input_vars(state.input_text, schema, parsed)
        state_params = state.metadata | state.store._data
        state.user_prompt.text = parsed.render(
            {
                **(params or {}),
                **state_params,
                **vars,
            }
        ).strip()
        return state

    return solve


def input_vars(input: str, schema: Schema, template: Template | None = None):
    if schema == "auto":
        if template is None:
            # Nothing to infer, assume single 'input' var
            return {"input": input}

        # Infer using template field names
        field_names = template.field_names()
        if not field_names:
            return {}

        if field_names == {"input"}:
            # If only input is referenced, include input as 'input' var
            return {"input": input}

        # Template references other vars - parse as YAML
        return vars_for_any(yaml.safe_load(input), input)

    if schema is str:
        return {"input": input}

    # Any other schema type required structured data
    parsed = yaml.safe_load(input)
    if inspect.isclass(schema) and issubclass(schema, BaseModel):
        data = schema.model_validate(parsed)
    else:
        data = TypeAdapter(schema).validate_python(parsed)
    return vars_for_any(data, input)


def vars_for_any(val: Any, input: str):
    if isinstance(val, dict):
        struct = val
    elif isinstance(val, BaseModel):
        struct = val.model_dump()
    elif isinstance(val, Sequence):
        struct = dict((str(i), val) for (i, val) in enumerate(val))
    else:
        struct = {"input": val}
    return {**struct, "_input": input}
