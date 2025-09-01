import redis

from config.config import config
from shared.redis_sdk.driver import DriverRedisSDK
from shared.redis_sdk.sim_clock import RedisClock


class RedisClient:
    """
    Shared Redis client for reuse across SDK modules.
    """

    _client: redis.Redis

    def __init__(self, host: str, port: int, db: int):
        self._client = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    @property
    def driver(self) -> DriverRedisSDK:
        return DriverRedisSDK(self._client)

    @property
    def clock(self) -> RedisClock:
        return RedisClock(self._client)

    def close(self):
        try:
            self._client.close()
        except Exception:
            pass


redis_client = RedisClient(host=config.redis.host, port=config.redis.port, db=config.redis.db)
