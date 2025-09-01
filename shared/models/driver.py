from typing import Optional

from pydantic import BaseModel, Field, FutureDatetime

from shared.models import Location, VehicleType


class Driver(BaseModel):
    id: int
    name: str
    vehicle_type: VehicleType
    busy: bool = False
    location: Location
    eta: Optional[FutureDatetime] = None
    rating: float = Field(..., ge=0, le=5)
