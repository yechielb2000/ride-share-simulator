from datetime import datetime
from typing import List, Optional

import redis

from shared.geo import distance
from shared.models import Driver, Location


class DriverRedisSDK:
    """
    General-purpose ACID-compliant Redis SDK for managing drivers.
    """
    _client: redis.client.Redis

    def __init__(self, client: redis.client.Redis) -> None:
        self._client = client

    def add(self, driver: Driver):
        """Add driver to Redis and GEO index."""
        pipe = self._client.pipeline()
        pipe.set(f"driver:{driver.id}", driver.model_dump_json())
        pipe.sadd("drivers:set", driver.id)
        pipe.geoadd("drivers:geo", (driver.location.lon, driver.location.lat, driver.id))
        if not driver.busy:
            pipe.sadd("drivers:available", driver.id)
        pipe.execute()

    def get(self, driver_id: str) -> Optional[Driver]:
        """Get a driver by ID."""
        data = self._client.get(f"driver:{driver_id}")
        if data:
            return Driver.model_validate(data)
        return None

    def list_all(self) -> List[Driver]:
        """Return all drivers."""
        driver_ids = self._client.smembers("drivers:set")
        return [self.get(driver_id) for driver_id in driver_ids if self.get(driver_id)]

    def list_available(self, vehicle_type: Optional[str] = None) -> List[Driver]:
        """
        Return available drivers, optionally filtered by vehicle type.
        """
        driver_ids = self._client.smembers("drivers:available")
        drivers = [self.get(driver_id) for driver_id in driver_ids if self.get(driver_id)]
        if vehicle_type:
            drivers = [d for d in drivers if d.vehicle_type == vehicle_type]
        return drivers

    def mark_busy(self, driver_id: int, free_time: datetime) -> bool:
        """
        Mark driver as busy and set free_time.
        Removes a driver from the available set.
        """
        key_driver = f"driver:{driver_id}"
        key_free_time = f"driver:{driver_id}:free_time"

        with self._client.pipeline() as pipe:
            while True:
                try:
                    pipe.watch(key_driver)
                    data = pipe.get(key_driver)
                    if not data:
                        pipe.unwatch()
                        return False
                    driver = Driver.model_validate(data)
                    if driver.busy:
                        pipe.unwatch()
                        return False

                    driver.busy = True
                    driver.eta = free_time

                    pipe.multi()
                    pipe.set(key_driver, driver.model_dump_json())
                    pipe.set(key_free_time, free_time.isoformat())
                    pipe.srem("drivers:available", driver_id)
                    pipe.execute()
                    return True
                except redis.WatchError:
                    pass  # retry transaction

    def mark_free(self, driver_id: str) -> bool:
        """
        Mark driver as free and re-add to the available set.
        Deletes the free_time key.
        """
        key_driver = f"driver:{driver_id}"
        key_free_time = f"driver:{driver_id}:free_time"

        with self._client.pipeline() as pipe:
            while True:
                try:
                    pipe.watch(key_driver)
                    data = pipe.get(key_driver)
                    if not data:
                        pipe.unwatch()
                        return False
                    driver = Driver.load_model(data)
                    driver.busy = False
                    driver.eta = None

                    pipe.multi()
                    pipe.set(key_driver, driver.model_dump_json())
                    pipe.delete(key_free_time)
                    pipe.sadd("drivers:available", driver_id)
                    pipe.execute()
                    return True
                except redis.WatchError:
                    pass  # retry transaction

    def get_locations(self, driver_ids: List[str]) -> dict[int, Location]:
        """
        Return {driver_id: Location} for the given driver IDs.
        """
        positions = self._client.geopos("drivers:geo", *driver_ids)
        return {
            int(did): Location(lat=pos[1], lon=pos[0])
            for did, pos in zip(driver_ids, positions)
            if pos
        }

    def get_distances(self, target: Location, driver_ids: List[str]) -> dict[int, float]:
        """
        Return {driver_id: distance_in_km} to the target location.
        """
        locations = self.get_locations(driver_ids)
        return {did: distance(loc, target) for did, loc in locations.items()}
