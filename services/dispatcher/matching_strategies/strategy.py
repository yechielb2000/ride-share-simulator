from abc import ABC, abstractmethod

from shared.models import Ride, Driver
from shared.models.driver import Drivers


class MatchingStrategy(ABC):
    """
    interface for all matching strategies.
    """

    @abstractmethod
    def match(self, ride: Ride, available_drivers: Drivers) -> Driver | None:
        """
        Given a ride and available drivers, return the best available driver or None.
        """
        raise NotImplementedError('please implement match')
