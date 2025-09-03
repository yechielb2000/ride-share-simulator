import threading
import time
from datetime import timedelta

from shared.logger import logger
from shared.redis_sdk.client import redis_client

TICK_INTERVAL_SECONDS = 1


def free_expired_drivers():
    """
    Iterate over busy drivers and free any whose ETA has passed.
    """
    for driver in redis_client.driver.list_unavailable():
        if driver.eta and driver.eta <= redis_client.clock.get():
            redis_client.driver.mark_free(driver.id)
            logger.info(f"Driver freed: {driver.id} (ETA {driver.eta.isoformat()})")


def tick_clock(delta: timedelta = timedelta(seconds=1)):
    """
    Advance the RedisClock by delta.
    """
    new_time = redis_client.clock.advance(delta)
    logger.debug(f"Clock advanced to {new_time.isoformat()}")


def clock_loop(tick_interval: float = TICK_INTERVAL_SECONDS):
    """
    The main loop of the Clock service: advance time and free drivers periodically.
    """
    logger.info("Clock service started")
    while True:
        tick_clock(timedelta(seconds=tick_interval))
        free_expired_drivers()
        time.sleep(tick_interval)


if __name__ == "__main__":
    clock_thread = threading.Thread(target=clock_loop, daemon=True)
    clock_thread.start()
    clock_thread.join()
