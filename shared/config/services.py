from enum import Enum
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class ClockConfig(BaseModel):
    advance_delta_seconds: int = 1


class StrategyType(str, Enum):
    NEAREST = "nearest"
    WEIGHTED = "weighted"


class DispatcherConfig(BaseSettings):
    group_id: str = "dispatcher"
    strategy: StrategyType


class DriverLoaderConfig(BaseModel):
    json_file: Path


class MetricsConfig(BaseModel):
    group_id: str = "metrics"
    host: str = "127.0.0.1"
    port: int = 8000


class RidesProducerConfig(BaseSettings):
    topic: str = "ride_requests"
    json_file: Path
    sim_speed: float = 5
