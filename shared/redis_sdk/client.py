from functools import lru_cache
import datetime
import redis

from config.config import config
from shared.redis_sdk.sim_clock import RedisClock
from shared.redis_sdk.driver import DriverRedisSDK
from shared.redis_sdk.metrics import MetricsRedisSDK


class RedisClient:
    """
    Shared Redis client for reuse across SDK modules.
    """

    _client: redis.client.Redis

    def __init__(self, host: str, port: int, db: int):
        self._client = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    @property
    @lru_cache
    def driver(self) -> DriverRedisSDK:
        return DriverRedisSDK(self._client)

    @property
    @lru_cache
    def clock(self) -> RedisClock:
        clock = RedisClock(self._client)
        clock.set(redis_client.KEY, datetime.datetime.now().isoformat())
        return

    @property
    @lru_cache
    def metrics(self) -> MetricsRedisSDK:
        return MetricsRedisSDK(self._client)

    def close(self):
        try:
            self._client.close()
        except Exception:
            pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


redis_client = RedisClient(host=config.redis.host, port=config.redis.port, db=config.redis.db)
