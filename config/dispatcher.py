from pydantic_settings import BaseSettings

from services.dispatcher.matching_strategies.strategy_factory import StrategyType


class DispatcherProducer(BaseSettings):
    topic: str = "assignments"


class DispatcherConfig(BaseSettings):
    group_id: str = "dispatcher"
    producer: DispatcherProducer
    strategy: StrategyType
