import math
from enum import Enum
from typing import Self

from pydantic import BaseModel

DEFAULT_SPEED_KMH = 30.0  # as per assignment


class VehicleType(str, Enum):
    PRIVATE = "private"
    SUV = "suv"


class Location(BaseModel):
    lat: float
    lon: float

    def distance(self, loc2: Self) -> float:
        """
        Checking straight-line (Euclidean) distance between the current location and the given location.
        Note: We are Using Euclidean distance since the assignment specifies 'straight-line distance'.
        """
        return math.dist([self.lat, self.lon], [loc2.lat, loc2.lon])

    def eta_seconds_from_target(self, loc2: Self, speed_kmh: float = DEFAULT_SPEED_KMH) -> float:
        return self.eta_from_target(loc2, speed_kmh) * 60 * 60  # for seconds

    def eta_from_target(self, loc2: Self, speed_kmh: float = DEFAULT_SPEED_KMH) -> float:
        return self.distance(loc2) / speed_kmh
