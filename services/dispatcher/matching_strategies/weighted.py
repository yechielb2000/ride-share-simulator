from services.dispatcher.matching_strategies.strategy import MatchingStrategy
from shared.models import Driver, Drivers, Ride


class WeightedScoreStrategy(MatchingStrategy):

    def match(self, ride: Ride, available_drivers: Drivers) -> Driver | None:
        return min(available_drivers, key=lambda d: abs(d.rating - ride.user_rating))
