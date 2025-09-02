import datetime

from pydantic import BaseModel


class Assignment(BaseModel):
    ride_id: str
    driver_id: str
    timestamp: datetime.datetime
