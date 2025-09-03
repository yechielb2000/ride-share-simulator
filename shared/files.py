from pathlib import Path
from typing import Iterator, TypeVar

import ijson
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def load_models_from_json(filepath: Path, ijson_key: str, model_cls: type[T]) -> Iterator[T]:
    """
    Yield T objects one by one from a JSON file.
    Expects JSON structure: { "<ijson_key>": [ {...}, {...} ] } where {...} structure = T
    """
    with open(filepath) as f:
        for driver_obj in ijson.items(f, f"{ijson_key}.item"):
            yield model_cls.model_validate(driver_obj)
