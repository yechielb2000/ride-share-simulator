import math

from shared.models import Location

DEFAULT_SPEED_KMH = 30.0  # as per assignment
MINUTES_PER_HOUR = 60.0


def distance(loc1: Location, loc2: Location) -> float:
    """
    Checking straight-line (Euclidean) distance between two locations.
    Note: We are Using Euclidean distance since the assignment specifies
    'straight-line distance', not geographic (Haversine).
    """
    return math.dist([loc1.lat, loc1.lon], [loc2.lat, loc2.lon])


def eta_minutes(loc1: Location, loc2: Location, speed_kmh: float = DEFAULT_SPEED_KMH) -> float:
    """
    Estimate travel time in minutes given two locations and a speed (km/h).
    """
    dist = distance(loc1, loc2)
    hours = dist / speed_kmh
    return hours * MINUTES_PER_HOUR
