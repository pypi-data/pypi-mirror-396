import re

from docstring_parser import Docstring, parse as parse_docstring


def parse_task_doc(doc: str) -> Docstring:
    # Hack the docstring to use `Input:` for args and `Output:` for returns`
    replacements = {
        "Args:": "Args_renamed:",
        "Returns:": "Returns_renamed:",
        "Input:": "Args:",
        "Output:": "Returns:",
    }
    doc = re.sub(
        r"^(\s*)({})$".format("|".join(replacements)),
        lambda m: m.group(1) + replacements[m.group(2)],
        doc,
        flags=re.MULTILINE,
    )
    return parse_docstring(doc)
