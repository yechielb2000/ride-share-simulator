import datetime

from pydantic import BaseModel, Field

from shared.models import Location, VehicleType


class Ride(BaseModel):
    id: int
    pickup: Location
    dropoff: Location
    vehicle_type: VehicleType
    timestamp: datetime.datetime
    user_rating: float = Field(..., ge=0, le=5)
