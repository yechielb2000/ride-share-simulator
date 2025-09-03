import datetime

from shared.config.config import config
from services.dispatcher.matching_strategies.strategy_factory import get_strategy
from shared.geo import eta_minutes
from shared.kafka import KafkaConsumer
from shared.logger import logger
from shared.models import Assignment, Ride, Driver
from shared.redis_sdk import redis_client

ride_consumer = KafkaConsumer[Ride](
    bootstrap_servers=config.kafka.bootstrap_servers,
    group_id=config.dispatcher.group_id,
    topic=config.rides_producer.topic,
    model_cls=Ride,
)

strategy = get_strategy(config.dispatcher.strategy)


def main():
    for ride in ride_consumer.consume():
        if redis_client.clock.get() < ride.timestamp:
            redis_client.clock.set(ride.timestamp)

        set_drivers_free()

        available_drivers = redis_client.driver.list_available()
        available_drivers = available_drivers.filter_by_vehicle_type(vehicle_type=ride.vehicle_type)
        if not available_drivers:
            logger.info("No available drivers")
            redis_client.metrics.add_unassigned(ride_id=ride.id)
            continue

        selected_driver = strategy(redis_client.driver).match(ride, available_drivers)
        if not selected_driver:
            logger.info("No suitable driver found for ride", ride_id=ride.id)
            redis_client.metrics.add_unassigned(ride_id=ride.id)
            continue

        set_drive_busy(ride, selected_driver)
        assignment = Assignment(
            ride_id=ride.id,
            ride_request_time=ride.timestamp,
            driver_id=selected_driver.id,
            timestamp=redis_client.clock.get()
        )
        redis_client.metrics.add_assignment(assignment)


def set_drivers_free():
    """
    set free drivers that are no longer busy
    """
    for driver in redis_client.driver.list_unavailable():
        # not sure if I need to check for driver.eta but for the sake of it...
        if driver.eta and driver.eta <= redis_client.clock.get():
            redis_client.driver.mark_free(driver.id)


def set_drive_busy(ride: Ride, driver: Driver):
    """
    Mark selected-driver as busy
    """
    pickup_eta = eta_minutes(driver.location, ride.pickup)
    dropoff_eta = eta_minutes(ride.pickup, ride.dropoff)
    free_time = redis_client.clock.get() + datetime.timedelta(minutes=pickup_eta + dropoff_eta)
    redis_client.driver.mark_busy(driver.id, free_time)


if __name__ == '__main__':
    main()
