from enum import Enum

from pydantic_settings import BaseSettings


class StrategyType(str, Enum):
    NEAREST = 'nearest'
    WEIGHTED = 'weighted'


class DispatcherConfig(BaseSettings):
    group_id: str = "dispatcher"
    strategy: StrategyType
