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
        current_time = redis_client.clock.get()
        if ride.timestamp < current_time:
            logger.info("Skipping past ride", ride_id=ride.id, ride_ts=ride.timestamp, clock=current_time)
            redis_client.metrics.add_unassigned(ride_id=ride.id)
            continue

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


def set_drive_busy(ride: Ride, driver: Driver):
    """
    Mark the driver as busy until the ride and pickup time is complete.
    """
    overall_travel_time = get_pickup_eta(ride, driver) + datetime.timedelta(seconds=ride.eta_seconds())
    redis_client.driver.mark_busy(driver.id, overall_travel_time)
    logger.info("Driver marked busy", ride_id=ride.id, driver_id=driver.id, eta=overall_travel_time)


def get_pickup_eta(ride: Ride, driver: Driver) -> datetime.datetime:
    """
    Calculate pickup ETA based on the driver's location and ride pickup point.
    """
    pickup_eta_seconds = driver.location.eta_seconds_from_target(ride.pickup)
    return ride.timestamp + datetime.timedelta(seconds=pickup_eta_seconds)


def assign(ride: Ride, selected_driver: Driver):
    """
    Create assignment, mark driver busy, and record metrics.
    """
    assignment = Assignment(
        ride_id=ride.id,
        ride_request_time=ride.timestamp,
        driver_id=selected_driver.id,
        pickup_time=get_pickup_eta(ride, selected_driver)
    )
    redis_client.metrics.add_assignment(assignment)
    redis_client.metrics.remove_unassigned(ride.id)
    set_drive_busy(ride, selected_driver)
    logger.info("Ride was assigned to driver", ride_id=ride.id, driver_id=selected_driver.id)


if __name__ == '__main__':
    main()
