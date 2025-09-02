import datetime

from config.config import config
from services.dispatcher.assignments_producer import AssignmentProducer
from services.dispatcher.matching_strategies.strategy_factory import get_strategy
from services.dispatcher.rides_consumer import RidesConsumer
from shared.geo import eta_minutes
from shared.models import Assignment, Ride, Driver
from shared.redis_sdk import redis_client

# TODO: not here! load drivers on lifecycle start

ride_consumer = RidesConsumer(
    bootstrap_servers=config.kafka.bootstrap_servers,
    group_id=config.dispatcher.group_id,
    topic=config.rides_producer.topic,
)
assignment_producer = AssignmentProducer(
    bootstrap_servers=config.kafka.bootstrap_servers,
    topic=config.dispatcher.producer.topic,
)

strategy = get_strategy(config.dispatcher.strategy)


def main():
    for ride in ride_consumer.consume():
        if redis_client.clock.get() < ride.timestamp:
            redis_client.clock.set(ride.timestamp)

        set_drivers_free()

        available_drivers = redis_client.driver.list_available(vehicle_type=ride.vehicle_type)
        if not available_drivers:
            # TODO: replace with log
            print(f"No available driver for ride {ride.id}")
            continue

        selected_driver = strategy(redis_client.driver).match(ride, available_drivers)
        if not selected_driver:
            # TODO: replace with log
            print(f"No suitable driver found for ride {ride.id}")
            continue

        set_drive_busy(ride, selected_driver)

        assignment = Assignment(
            ride_id=ride.id,
            driver_id=selected_driver.id,
            timestamp=redis_client.clock.get()
        )
        assignment_producer.send(assignment)


def set_drivers_free():
    """
    set free drivers that are no longer busy
    """
    for driver in redis_client.driver.list():
        if driver.busy and driver.eta and driver.eta <= redis_client.clock.get():
            redis_client.driver.mark_free(driver.id)


def set_drive_busy(ride: Ride, driver: Driver):
    """
    Mark selected-driver as busy
    """
    pickup_eta = eta_minutes(driver.location, ride.pickup_location)
    dropoff_eta = eta_minutes(ride.pickup_location, ride.dropoff_location)
    free_time = redis_client.clock.get() + datetime.timedelta(minutes=pickup_eta + dropoff_eta)
    redis_client.driver.mark_busy(driver.id, free_time)


if __name__ == '__main__':
    main()
