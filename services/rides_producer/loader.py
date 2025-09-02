from pathlib import Path
from typing import Iterator

import ijson

from shared.models import Ride


def load_rides(json_file: Path) -> Iterator[Ride]:
    """
    Yield Ride objects one by one from a JSON file without loading all into memory.
    Expects JSON structure: { "rides": [ {...}, {...} ] }
    """
    with open(json_file) as f:
        for ride_obj in ijson.items(f, "rides.item"):
            yield Ride.model_validate(ride_obj)
