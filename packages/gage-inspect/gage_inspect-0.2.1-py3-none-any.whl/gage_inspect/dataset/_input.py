from typing import Any

import yaml


def structured_input(obj: Any | None = None, **attrs):
    """Returns a string that can be used as sample input for structured data.

    If specified, `obj` must provide `model_dump` (e.g. instances of
    Pydantic models). Otherwise specify structured data fields using
    keyword values.
    """
    if obj:
        try:
            model_dump = getattr(obj, "model_dump")
        except AttributeError:
            raise TypeError("obj must provide `model_dump` method")
        else:
            obj = model_dump()
    else:
        obj = attrs
    return yaml.dump(obj, default_flow_style=False).strip()
