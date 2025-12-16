def docstring_short_description(doc: str) -> str | None:
    from docstring_parser import parse

    return parse(doc).short_description


def pkg_version(pkg: str) -> str:
    from importlib.metadata import version

    return version(pkg)


def pkg_path(pkg: str) -> str:
    import os
    from importlib import import_module

    mod = import_module(pkg)
    return os.path.dirname(getattr(mod, "__file__"))
