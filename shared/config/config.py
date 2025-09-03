import threading
from pathlib import Path
from typing import Self

import yaml
from pydantic import PrivateAttr
from pydantic_settings import BaseSettings

from shared.config.clock import ClockConfig
from shared.config.dispatcher import DispatcherConfig
from shared.config.drivers_loader import DriverLoaderConfig
from shared.config.metrics import MetricsConfig
from shared.config.rides_producer import RidesProducerConfig
from shared.logger import logger

CONFIG_PATH = Path(__file__).resolve().parent / "config.yaml"


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

    _instance: Self = PrivateAttr(default=None)
    _lock: threading.Lock = PrivateAttr(default_factory=threading.Lock)

    @classmethod
    def reload_config(cls):
        with cls._lock:
            new_config = cls.from_yaml()
            global config
            config = new_config
            logger.info("Configuration reloaded successfully")

    @classmethod
    def from_yaml(cls, path: Path = CONFIG_PATH):
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path) as f:
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


config: AppConfig = AppConfig.from_yaml()
