import datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class Assignment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    ride_id: str
    driver_id: str
    pickup_time: datetime.datetime
    ride_request_time: datetime.datetime

    def average_pickup_eta_minutes(self) -> float:
        """
        Provide average pickup estimated time arrival in minutes.
        """
        return abs(self.pickup_time - self.ride_request_time).total_seconds() / 60


class Assignments(list[Assignment]):

    def average_pickup_time(self) -> float:
        """
        Return average pickup time in minutes.
        """
        avg_eta = 0.0
        if self:
            etas = [assignment.average_pickup_eta_minutes() for assignment in self]
            avg_eta = sum(etas) / len(etas)
        return avg_eta
