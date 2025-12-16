import os
from io import TextIOWrapper
from pathlib import Path
from typing import Any

from yaml import load_all

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from inspect_ai._util.file import file
from inspect_ai.dataset._dataset import (
    Dataset,
    DatasetReader,
    FieldSpec,
    MemoryDataset,
    RecordToSample,
)
from inspect_ai.dataset._sources.util import resolve_sample_files
from inspect_ai.dataset._util import (
    data_to_samples,
    record_to_sample_fn,
    shuffle_choices_if_requested,
)


def yaml_dataset(
    yaml_file: str,
    sample_fields: FieldSpec | RecordToSample | None = None,
    auto_id: bool = False,
    shuffle: bool = False,
    seed: int | None = None,
    shuffle_choices: bool | int | None = None,
    limit: int | None = None,
    encoding: str = "utf-8",
    name: str | None = None,
    fs_options: dict[str, Any] = {},
) -> Dataset:
    r"""Read dataset from a YAML file.

    Read a dataset from a YAML file containing objects as separate documents, each
    separated by `---`. These objects may already be formatted as `Sample` instances,
    or may require some mapping using the `sample_fields` argument.

    Args:
      yaml_file: Path to YAML file. Can be a local filesystem path or
        a path to an S3 bucket (e.g. "s3://my-bucket"). Use `fs_options`
        to pass arguments through to the `S3FileSystem` constructor.
      sample_fields: Method of mapping underlying
        fields in the data source to `Sample` objects. Pass `None` if the data is already
        stored in `Sample` form (i.e. object with "input" and "target" fields); Pass a
        `FieldSpec` to specify mapping fields by name; Pass a `RecordToSample` to
        handle mapping with a custom function that returns one or more samples.
      auto_id: Assign an auto-incrementing ID for each sample.
      shuffle: Randomly shuffle the dataset order.
      seed: Seed used for random shuffle.
      shuffle_choices: Whether to shuffle the choices. If an int is passed, this will be used as the seed when shuffling.
      limit: Limit the number of records to read.
      encoding: Text encoding for file (defaults to "utf-8").
      name: Optional name for dataset (for logging). If not specified,
        defaults to the stem of the filename.
      fs_options: Optional. Additional arguments to pass through
        to the filesystem provider (e.g. `S3FileSystem`). Use `{"anon": True }`
        if you are accessing a public S3 bucket with no credentials.

    Returns:
        Dataset read from JSON file.
    """
    # resolve data_to_sample function
    data_to_sample = record_to_sample_fn(sample_fields)

    # read and convert samples
    with file(yaml_file, "r", encoding=encoding, fs_options=fs_options) as f:
        name = name if name else Path(yaml_file).stem
        dataset = MemoryDataset(
            samples=data_to_samples(yaml_dataset_reader(f), data_to_sample, auto_id),
            name=name,
            location=os.path.abspath(yaml_file),
        )

        # resolve relative file paths
        resolve_sample_files(dataset)

        # shuffle if requested
        if shuffle:
            dataset.shuffle(seed=seed)

        shuffle_choices_if_requested(dataset, shuffle_choices)

        # limit if requested
        if limit:
            return dataset[0:limit]

    return dataset


def yaml_dataset_reader(file: TextIOWrapper) -> DatasetReader:
    for doc in load_all(file, Loader=Loader):
        if isinstance(doc, dict):
            yield doc
        elif isinstance(doc, list):
            yield dict((str(i), val) for i, val in enumerate(doc))
        elif isinstance(doc, str):
            yield {"input": doc.strip()}
        else:
            yield {"input": doc}
