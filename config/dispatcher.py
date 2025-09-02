from enum import Enum

from pydantic_settings import BaseSettings


class StrategyType(str, Enum):
    NEAREST = 'nearest'
    WEIGHTED = 'weighted'


class DispatcherProducer(BaseSettings):
    topic: str = "assignments"


class DispatcherConfig(BaseSettings):
    group_id: str = "dispatcher"
    producer: DispatcherProducer = DispatcherProducer()
    strategy: StrategyType
