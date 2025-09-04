import datetime

import redis

from shared.logger import logger


class RedisClock:
    KEY = "sim_clock"

    def __init__(self, pool: redis.ConnectionPool) -> None:
        self._pool = pool

    @property
    def client(self) -> redis.Redis:
        return redis.Redis(connection_pool=self._pool)

    def set(self, dt: datetime.datetime) -> None:
        """Set the clock to a specific datetime."""
        self.client.set(self.KEY, dt.isoformat())
        logger.info(f"Clock set to {dt.isoformat()}")

    def set_now_once(self):
        """Set the clock now but only if the key doesn't exist."""
        if self.client.get(self.KEY) is None:
            self.set(datetime.datetime.now(datetime.UTC))

    def get(self) -> datetime.datetime:
        ts = self.client.get(self.KEY)
        if not ts:
            self.set_now_once()
            logger.info("Clock not set, setting to now")
            return self.get()
        return datetime.datetime.fromisoformat(ts)

    def advance(self, delta: datetime.timedelta) -> datetime.datetime | None:
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
                pass
