from services.dispatcher.matching_strategies.strategy import MatchingStrategy
from shared.models import Driver, Ride
from shared.models.driver import Drivers


class NearestDriverStrategy(MatchingStrategy):

    def match(self, ride: Ride, available_drivers: Drivers) -> Driver | None:
        return min(available_drivers, key=lambda d: d.location.distance(ride.pickup))
