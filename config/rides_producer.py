from pathlib import Path

from pydantic_settings import BaseSettings


class RidesProducerConfig(BaseSettings):
    topic: str
    json_file: Path
    sim_speed: float = 60.0  # probably should delete that
