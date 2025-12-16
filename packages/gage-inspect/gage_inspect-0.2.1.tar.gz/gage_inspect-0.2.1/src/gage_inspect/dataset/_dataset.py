from typing import Any, Callable, TypeVar
from inspect_ai.dataset import Dataset, Sample
from pydantic import BaseModel

ImpliedDataset = list[Sample | str | dict[str, Any]]

DatasetType = TypeVar("DatasetType", bound=Callable[..., Dataset | ImpliedDataset])


class DatasetInfo(BaseModel):
    """Dataset information (file, name, and attributes)."""

    file: str
    """Dataset type source location."""

    name: str
    """Dataset name (defaults to function name)"""

    attribs: dict[str, Any]
    """Dataset attributes (arguments passed to `@dataset`)"""

    def __str__(self) -> str:
        return f"{self.file}@{self.name}"

    def __hash__(self) -> int:
        return hash(
            (self.file, self.name)
            + tuple(self.attribs.keys())
            + tuple(self.attribs.values())
        )
