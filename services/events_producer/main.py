from datetime import datetime, timezone
from time import sleep

from services.events_producer.config import config
from services.events_producer.loader import load_rides
from services.events_producer.producer import RideProducer


def main():
    ride_producer = RideProducer(config.kafka.bootstrap_servers, config.kafka.topic)
    start_time = datetime.now(timezone.utc)

    for ride in load_rides(config.producer.json_file):
        delta = (ride.timestamp - start_time).total_seconds()
        sleep_time = max(0, delta / config.producer.sim_speed)
        sleep(sleep_time)
        ride_producer.produce_ride(ride)


if __name__ == "__main__":
    main()
