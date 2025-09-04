from collections.abc import Iterator
from pathlib import Path

import ijson
from pydantic import BaseModel


def load_models_from_json(filepath: Path, ijson_key: str, model_cls: type[BaseModel]) -> Iterator[BaseModel]:
    """
    Yield T objects one by one from a JSON file.
    Expects JSON structure: { "<ijson_key>": [ {...}, {...} ] } where {...} Structure = T
    """
    with Path.open(filepath) as f:
        for driver_obj in ijson.items(f, f"{ijson_key}.item"):
            yield model_cls.model_validate(driver_obj)
