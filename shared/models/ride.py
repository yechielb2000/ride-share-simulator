import datetime

from pydantic import BaseModel, Field

from shared.geo import eta_seconds_from_target
from shared.models import Location, VehicleType


class Ride(BaseModel):
    id: str
    pickup: Location
    dropoff: Location
    vehicle_type: VehicleType
    timestamp: datetime.datetime
    user_rating: float = Field(..., ge=0, le=5)

    def eta_seconds(self) -> float:
        """
        Estimate travel time in seconds.
        """
        return self.pickup.eta_seconds_from_target(self.dropoff)


class Rides(list[Ride]):
    pass
