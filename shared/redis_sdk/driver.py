from datetime import datetime

import redis

from shared.models import Driver, Drivers


class DriverRedisSDK:

    def __init__(self, pool: redis.ConnectionPool) -> None:
        self._pool = pool

    @property
    def client(self) -> redis.Redis:
        return redis.Redis(connection_pool=self._pool)

    def add(self, driver: Driver):
        pipe = self.client.pipeline()
        pipe.set(f"driver:{driver.id}", driver.model_dump_json())
        pipe.sadd("drivers:set", driver.id)
        if not driver.busy:
            pipe.sadd("drivers:available", driver.id)
        pipe.execute()

    def get(self, driver_id: str) -> Driver | None:
        """Get a driver by ID."""
        data = self.client.get(f"driver:{driver_id}")
        if data:
            return Driver.model_validate_json(data)
        return None

    def list_all(self) -> Drivers:
        drivers = Drivers()
        driver_ids = self.client.smembers("drivers:set")
        for driver_id in driver_ids:
            driver = self.get(driver_id)
            if driver:
                drivers.append(driver)
        return drivers

    def list_available(self) -> Drivers:
        driver_ids = self.client.smembers("drivers:available")
        drivers = Drivers()
        for driver_id in driver_ids:
            driver = self.get(driver_id)
            if driver:
                drivers.append(driver)
        return drivers

    def list_unavailable(self) -> Drivers:
        all_driver_ids = self.list_all()
        available_ids = self.list_available()
        return all_driver_ids - available_ids

    def mark_busy(self, driver_id: int, free_time: datetime):
        """
        Mark the driver as busy and set free_time.
        Removes a driver from the available set.
        """
        key_driver = f"driver:{driver_id}"
        key_free_time = f"driver:{driver_id}:free_time"

        with self.client.pipeline() as pipe:
            while True:
                try:
                    pipe.watch(key_driver)
                    data = pipe.get(key_driver)
                    if not data:
                        pipe.unwatch()
                        break
                    driver = Driver.model_validate_json(data)
                    if driver.busy:
                        pipe.unwatch()
                        break

                    driver.busy = True
                    driver.eta = free_time

                    pipe.multi()
                    pipe.set(key_driver, driver.model_dump_json())
                    pipe.set(key_free_time, free_time.isoformat())
                    pipe.srem("drivers:available", driver_id)
                    pipe.execute()
                    break
                except redis.WatchError:
                    pass

    def mark_free(self, driver_id: str):
        """
        Mark the driver as free and re-add to the available set.
        Deletes the free_time key.
        """
        key_driver = f"driver:{driver_id}"
        key_free_time = f"driver:{driver_id}:free_time"

        with self.client.pipeline() as pipe:
            while True:
                try:
                    pipe.watch(key_driver)
                    data = pipe.get(key_driver)
                    if not data:
                        pipe.unwatch()
                        break
                    driver = Driver.model_validate_json(data)
                    driver.busy = False
                    driver.eta = None

                    pipe.multi()
                    pipe.set(key_driver, driver.model_dump_json())
                    pipe.delete(key_free_time)
                    pipe.sadd("drivers:available", driver_id)
                    pipe.execute()
                    break
                except redis.WatchError:
                    pass
