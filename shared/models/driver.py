import datetime
from collections.abc import Iterable
from typing import Self

from pydantic import BaseModel, Field

from shared.models import Location, VehicleType


class Driver(BaseModel):
    id: str
    name: str
    vehicle_type: VehicleType
    busy: bool = False
    location: Location
    eta: datetime.datetime | None = None
    rating: float = Field(..., ge=0, le=5)


class Drivers(list[Driver]):

    def filter_by_vehicle_type(self, vehicle_type: VehicleType) -> Self:
        return type(self)(driver for driver in self if driver.vehicle_type == vehicle_type)

    def __sub__(self, other: Iterable[Driver]) -> Self:
        """
        Comparison is by driver.id.
        """
        other_ids = {driver.id for driver in other}
        return type(self)(driver for driver in self if driver.id not in other_ids)
