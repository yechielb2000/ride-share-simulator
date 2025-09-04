import datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class Assignment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    ride_id: str
    driver_id: str
    pickup_time: datetime.datetime
    ride_request_time: datetime.datetime

    def average_pickup_eta(self) -> float:
        return abs(self.pickup_time - self.ride_request_time).total_seconds()


class Assignments(list[Assignment]):

    def average_pickup_time(self) -> float:
        avg_eta = 0.0
        if self:
            etas = [assignment.average_pickup_eta() for assignment in self]
            avg_eta = sum(etas) / len(etas)
        return avg_eta
