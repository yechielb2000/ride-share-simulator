from pydantic import BaseModel, Field

from shared.models import Location, VehicleType


class Driver(BaseModel):
    id: int
    name: str
    vehicle_type: VehicleType
    busy: bool = False
    location: Location
    rating: float = Field(..., ge=0, le=5)
