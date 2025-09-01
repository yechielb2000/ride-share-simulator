from datetime import datetime
from typing import List

import redis

from shared.models import Driver


class DriverRedisSDK:
    """
    ACID-compliant CRUD SDK for Driver
    """
    _client: redis.Redis

    def __init__(self, client: redis.Redis):
        self._client = client

    def add(self, driver: Driver):
        pipe = self._client.pipeline()
        pipe.set(f"driver:{driver.id}", driver.json())
        pipe.sadd("drivers:set", driver.id)
        pipe.execute()

    def get(self, driver_id: int) -> Driver | None:
        data = self._client.get(f"driver:{driver_id}")
        if data:
            return Driver.load_model(data)
        return None

    def list(self) -> list[Driver]:
        driver_ids = self._client.smembers("drivers:set")
        return [self.get(int(did)) for did in driver_ids if self.get(int(did))]

    def list_available(self) -> List[Driver]:
        return [d for d in self.list() if not d.busy]

    def mark_busy(self, driver_id: int, free_time: datetime) -> bool:
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
                    if driver.busy:
                        pipe.unwatch()
                        return False

                    driver.busy = True
                    driver.eta = free_time.isoformat()

                    pipe.multi()
                    pipe.set(key_driver, driver.json())
                    pipe.set(key_free_time, free_time.isoformat())
                    pipe.execute()
                    return True
                except redis.WatchError:
                    return False

    def mark_free(self, driver_id: int) -> bool:
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
                    pipe.set(key_driver, driver.json())
                    pipe.delete(key_free_time)
                    pipe.execute()
                    return True
                except redis.WatchError:
                    return False
