import threading
from pathlib import Path
from typing import ClassVar, Self

import yaml
from pydantic_settings import BaseSettings

from shared.config.services import (
    ClockConfig,
    DispatcherConfig,
    DriverLoaderConfig,
    MetricsConfig,
    RidesProducerConfig,
)
from shared.logger import logger

CONFIG_PATH = Path(__file__).resolve().parent / "config.yaml"
_config_lock = threading.Lock()


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
    clock: ClockConfig

    _instance: ClassVar[Self | None] = None

    @classmethod
    def instance(cls) -> Self:
        if cls._instance is None:
            with _config_lock:
                if cls._instance is None:
                    cls._instance = cls.from_yaml()
        return cls._instance

    @classmethod
    def reload_config(cls):
        with _config_lock:
            cls._instance = cls.from_yaml()
            logger.info("Configuration reloaded successfully")

    @classmethod
    def from_yaml(cls, path: Path = CONFIG_PATH):
        if not path.exists():
            msg = f"Config file not found: {path}"
            raise FileNotFoundError(msg)

        with Path.open(path) as f:
            cfg = yaml.safe_load(f)

        return cls(
            kafka=KafkaConfig(**cfg.get("kafka", {})),
            redis=RedisConfig(**cfg.get("redis", {})),
            metrics=MetricsConfig(**cfg.get("metrics", {})),
            clock=ClockConfig(**cfg.get("clock", {})),
            drivers_loader=DriverLoaderConfig(**cfg["drivers_loader"]),
            rides_producer=RidesProducerConfig(**cfg["rides_producer"]),
            dispatcher=DispatcherConfig(**cfg["dispatcher"]),
        )


config = AppConfig.instance()
