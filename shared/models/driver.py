from typing import Optional, Self

from pydantic import BaseModel, Field, FutureDatetime

from shared.models import Location, VehicleType


class Driver(BaseModel):
    id: str
    name: str
    vehicle_type: VehicleType
    busy: bool = False
    location: Location
    eta: Optional[FutureDatetime] = None
    rating: float = Field(..., ge=0, le=5)


class Drivers(list[Driver]):

    def filter_by_vehicle_type(self, vehicle_type: VehicleType) -> Self:
        return type(self)(driver for driver in self if driver.vehicle_type == vehicle_type)
