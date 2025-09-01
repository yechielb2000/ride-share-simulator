from pathlib import Path

import yaml
from pydantic_settings import BaseSettings


class KafkaConfig(BaseSettings):
    bootstrap_servers: str
    rides_topic: str


class RidesProducerConfig(BaseSettings):
    json_file: Path
    sim_speed: float = 60.0  # NOTE: 1 real second = 1 simulated minute


class AppConfig(BaseSettings):
    kafka: KafkaConfig
    rides_producer: RidesProducerConfig

    @classmethod
    def from_yaml(cls, filename: str = "config.yaml"):
        base_dir = Path(__file__).parent.resolve()
        path = base_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path) as f:
            cfg = yaml.safe_load(f)

        return cls(
            kafka=KafkaConfig(**cfg["kafka"]),
            rides_producer=RidesProducerConfig(**cfg["rides_producer"])
        )


config: AppConfig = AppConfig.from_yaml()
