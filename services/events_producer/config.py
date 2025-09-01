from pathlib import Path

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


class KafkaConfig(BaseSettings):
    bootstrap_servers: str = Field(..., env="KAFKA_BOOTSTRAP")
    topic: str = Field(..., env="KAFKA_TOPIC")


class ProducerConfig(BaseSettings):
    json_file: Path = Field(..., env="PRODUCER_JSON_FILE")
    sim_speed: float = Field(60.0, env="SIM_SPEED")  # NOTE: 1 real second = 1 simulated minute


class AppConfig(BaseSettings):
    kafka: KafkaConfig
    producer: ProducerConfig

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
            producer=ProducerConfig(**cfg["producer"])
        )


config = AppConfig.from_yaml()
