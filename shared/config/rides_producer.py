from pathlib import Path

from pydantic_settings import BaseSettings


class RidesProducerConfig(BaseSettings):
    topic: str = "ride_requests"
    json_file: Path
    sim_speed: float = 5
