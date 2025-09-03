from typing import Optional

from services.dispatcher.matching_strategies.strategy import MatchingStrategy
from shared.models import Ride, Driver
from shared.models.driver import Drivers


class NearestDriverStrategy(MatchingStrategy):

    def match(self, ride: Ride, available_drivers: Drivers) -> Optional[Driver]:
        driver_ids = [d.id for d in available_drivers]
        distances = self.driver_sdk.get_distances(ride.pickup, driver_ids)
        best_id = str(min(distances, key=distances.get))
        return self.driver_sdk.get(best_id)
