from typing import Optional

from services.dispatcher.matching_strategies.strategy import MatchingStrategy
from shared.models import Ride, Driver, Drivers


class WeightedScoreStrategy(MatchingStrategy):

    def match(self, ride: Ride, available_drivers: Drivers) -> Optional[Driver]:
        return min(available_drivers, key=lambda d: abs(d.rating - ride.user_rating))
