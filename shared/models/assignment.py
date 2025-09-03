import datetime

from pydantic import BaseModel


class Assignment(BaseModel):
    ride_id: str
    driver_id: str
    timestamp: datetime.datetime
    ride_request_time: datetime.datetime

    @property
    def id(self):
        """The actual assignment id is the ride_id."""
        return self.ride_id

    def average_pickup_eta_minutes(self) -> float:
        """
        Provide average pickup estimated time arrival in minutes.
        """
        return abs(self.timestamp - self.ride_request_time).total_seconds() / 60


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
