from abc import ABC, abstractmethod

from shared.models import Ride, Driver
from shared.models.driver import Drivers
from shared.redis_sdk import DriverRedisSDK


class MatchingStrategy(ABC):
    """
    interface for all matching strategies.
    """

    def __init__(self, driver_sdk: DriverRedisSDK):
        self.driver_sdk = driver_sdk

    @abstractmethod
    def match(self, ride: Ride, available_drivers: Drivers) -> Driver | None:
        """
        Given a ride and available drivers, return the best available driver or None.
        """
        raise NotImplementedError('please implement match')
