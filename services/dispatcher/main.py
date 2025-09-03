import datetime

from services.dispatcher.matching_strategies.strategy_factory import get_strategy
from shared.config.config import config
from shared.kafka import KafkaConsumer
from shared.logger import logger
from shared.models import Ride, Driver, Assignment
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

        assign(ride, selected_driver)


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
    overall_travel_time = get_pickup_eta(ride, driver) + datetime.timedelta(seconds=ride.eta_seconds())
    redis_client.driver.mark_busy(driver.id, overall_travel_time)
    logger.info("Driver marked busy", ride_id=ride.id, driver_id=driver.id, eta=overall_travel_time)


def get_pickup_eta(ride: Ride, driver: Driver) -> datetime.datetime:
    pickup_eta = driver.location.eta_seconds_from_target(ride.pickup)
    return ride.timestamp + datetime.timedelta(seconds=pickup_eta)


def assign(ride: Ride, selected_driver: Driver):
    pickup_eta = get_pickup_eta(ride, selected_driver)

    assignment = Assignment(
        ride_id=ride.id,
        ride_request_time=ride.timestamp,
        driver_id=selected_driver.id,
        timestamp=pickup_eta
    )
    redis_client.metrics.add_assignment(assignment)
    set_drive_busy(ride, selected_driver)
    logger.info("Ride was assigned to driver", ride_id=ride.id, driver_id=selected_driver.id)


if __name__ == '__main__':
    main()
