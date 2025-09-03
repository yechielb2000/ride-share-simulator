from datetime import datetime, timedelta

import redis

from shared.logger import logger


class RedisClock:
    """
    Shared simulation clock stored in Redis.
    """
    KEY = "sim_clock"

    def __init__(self, pool: redis.ConnectionPool) -> None:
        self._pool = pool

    @property
    def client(self) -> redis.Redis:
        return redis.Redis(connection_pool=self._pool)

    def set(self, dt: datetime) -> None:
        """Set the clock to a specific datetime."""
        self.client.set(self.KEY, dt.isoformat())
        logger.info(f"Clock set to {dt.isoformat()}")

    def set_now_once(self):
        """Set the clock to now but only if the key doesn't exist."""
        if self.client.get(self.KEY) is None:
            self.set(datetime.now())

    def get(self) -> datetime:
        ts = self.client.get(self.KEY)
        if not ts:
            raise ValueError(f"could not get timestamp from clock (keyname: {self.KEY})")
        return datetime.fromisoformat(ts)

    def advance(self, delta: timedelta) -> datetime | None:
        """Atomically advance the clock by delta."""
        while True:
            try:
                with self.client.pipeline() as pipe:
                    pipe.watch(self.KEY)
                    current = self.get()
                    new_time = current + delta
                    pipe.multi()
                    pipe.set(self.KEY, new_time.isoformat())
                    pipe.execute()
                    return new_time
            except redis.WatchError:
                logger.exception("Watch error")
