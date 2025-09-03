from pathlib import Path

import yaml
from pydantic_settings import BaseSettings

from shared.config.dispatcher import DispatcherConfig
from shared.config.drivers_loader import DriverLoaderConfig
from shared.config.metrics import MetricsConfig
from shared.config.rides_producer import RidesProducerConfig


class KafkaConfig(BaseSettings):
    bootstrap_servers: str = "kafka:9092"


class RedisConfig(BaseSettings):
    host: str = "redis"
    port: int = 6379
    db: int = 0


class AppConfig(BaseSettings):
    kafka: KafkaConfig
    redis: RedisConfig
    rides_producer: RidesProducerConfig
    dispatcher: DispatcherConfig
    metrics: MetricsConfig
    drivers_loader: DriverLoaderConfig

    @classmethod
    def from_yaml(cls, filename: str = "config.yaml"):
        base_dir = Path(__file__).parent.resolve()
        path = base_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path) as f:
            cfg = yaml.safe_load(f)

        return cls(
            kafka=KafkaConfig(**cfg["kafka"]) if cfg.get("kafka") else KafkaConfig(),
            redis=RedisConfig(**cfg["redis"]) if cfg.get("redis") else RedisConfig(),
            metrics=MetricsConfig(**cfg["metrics"]) if cfg.get("metrics") else MetricsConfig(),
            drivers_loader=DriverLoaderConfig(**cfg["drivers_loader"]),
            rides_producer=RidesProducerConfig(**cfg["rides_producer"]),
            dispatcher=DispatcherConfig(**cfg["dispatcher"])
        )


config: AppConfig = AppConfig.from_yaml()
