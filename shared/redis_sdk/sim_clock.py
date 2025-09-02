from datetime import datetime, timedelta

import redis


class RedisClock:
    """
    Shared simulation clock stored in Redis.
    """
    _client: redis.client.Redis
    KEY = "sim_clock"

    def __init__(self, client: redis.client.Redis):
        self._client = client

    def set(self, dt: datetime):
        """Set the clock to a specific datetime."""
        self._client.set(self.KEY, dt.isoformat())

    def get(self) -> datetime:
        ts = self._client.get(self.KEY)
        if ts:
            if isinstance(ts, bytes):
                return datetime.fromisoformat(ts.decode())
        raise ValueError(f"could not get timestamp from clock (keyname: {self.KEY})")

    def advance(self, delta: timedelta) -> datetime | None:
        """Atomically advance the clock by delta."""
        while True:
            try:
                with self._client.pipeline() as pipe:
                    pipe.watch(self.KEY)
                    current = self.get()
                    new_time = current + delta
                    pipe.multi()
                    pipe.set(self.KEY, new_time.isoformat())
                    pipe.execute()
                    return new_time
            except redis.WatchError:
                pass
