from pydantic import AwareDatetime
from pydantic import BaseModel, Field

from shared.models import Location, VehicleType


class Ride(BaseModel):
    id: int
    pickup: Location
    dropoff: Location
    vehicle_type: VehicleType
    timestamp: AwareDatetime
    user_rating: float = Field(..., ge=0, le=5)
