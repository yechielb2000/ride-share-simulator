from enum import Enum

from pydantic import BaseModel


class Location(BaseModel):
    lat: float
    lon: float


class VehicleType(str, Enum):
    PRIVATE = 'private'
    SUV = 'suv'
