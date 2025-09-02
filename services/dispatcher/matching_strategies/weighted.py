from typing import Optional

from services.dispatcher.matching_strategies.strategy import MatchingStrategy
from shared.models import Ride, Driver
from shared.redis_sdk import DriverRedisSDK


class WeightedScoreStrategy(MatchingStrategy):
    def __init__(self, driver_sdk: DriverRedisSDK, alpha: float = 0.7, beta: float = 0.3):
        super().__init__(driver_sdk)
        self.driver_sdk = driver_sdk
        self.alpha = alpha
        self.beta = beta

    def match(self, ride: Ride, available_drivers: list[Driver]) -> Optional[Driver]:
        driver_ids = [d.id for d in available_drivers]
        distances = self.driver_sdk.get_distances(ride.pickup_location, driver_ids)
        best_driver = max(
            available_drivers,
            key=lambda d: -self.alpha * distances[d.id] + self.beta * d.rating
        )
        return best_driver
