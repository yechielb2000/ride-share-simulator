from services.dispatcher.matching_strategies.nearest import NearestDriverStrategy
from services.dispatcher.matching_strategies.strategy import MatchingStrategy
from services.dispatcher.matching_strategies.weighted import WeightedScoreStrategy
from shared.config.services import StrategyType

STRATEGIES: dict[StrategyType, type[MatchingStrategy]] = {
    StrategyType.NEAREST: NearestDriverStrategy,
    StrategyType.WEIGHTED: WeightedScoreStrategy,
}


def get_strategy(strategy_type: StrategyType) -> type[MatchingStrategy]:
    strategy = STRATEGIES.get(strategy_type)
    if not strategy:
        msg = f"strategy_type must be one of {STRATEGIES.keys()}"
        raise ValueError(msg)
    return strategy
