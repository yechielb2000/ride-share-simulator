import threading

import redis

from shared.config.config import config
from shared.logger import logger
from shared.redis_sdk.driver import DriverRedisSDK
from shared.redis_sdk.metrics import MetricsRedisSDK
from shared.redis_sdk.sim_clock import RedisClock


class RedisClient:
    """
    Shared Redis client for reuse across SDK modules.
    """

    def __init__(self, host: str, port: int, db: int):
        self._pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            decode_responses=True
        )
        self._driver = DriverRedisSDK(self._pool)
        self._clock = RedisClock(self._pool)
        self._metrics = MetricsRedisSDK(self._pool)
        self._lock = threading.Lock()

    @property
    def pool(self):
        """Get connection pool and recreate if config changed"""
        with self._lock:
            current_host = self._pool.connection_kwargs['host']
            current_port = self._pool.connection_kwargs['port']
            current_db = self._pool.connection_kwargs['db']

            if (current_host != config.redis.host or
                    current_port != config.redis.port or
                    current_db != config.redis.db):
                logger.debug("Recreating Redis connection pool")
                self._pool = redis.ConnectionPool(
                    host=config.redis.host,
                    port=config.redis.port,
                    db=config.redis.db,
                    decode_responses=True
                )

                self._driver = DriverRedisSDK(self._pool)
                self._clock = RedisClock(self._pool)
                self._metrics = MetricsRedisSDK(self._pool)

        return self._pool

    @property
    def driver(self) -> DriverRedisSDK:
        return self._driver

    @property
    def clock(self) -> RedisClock:
        return self._clock

    @property
    def metrics(self) -> MetricsRedisSDK:
        return self._metrics

    def close(self):
        try:
            self._pool.disconnect()
        except Exception:
            pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


redis_client = RedisClient(host=config.redis.host, port=config.redis.port, db=config.redis.db)
