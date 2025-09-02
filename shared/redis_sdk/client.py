from functools import lru_cache

import redis

from config.config import config
from shared.redis_sdk import DriverRedisSDK, MetricsRedisSDK, RedisClock


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
        return RedisClock(self._client)

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
