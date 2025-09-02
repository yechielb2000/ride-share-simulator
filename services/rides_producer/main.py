import datetime
from time import sleep

from config.config import config
from services.rides_producer.loader import load_rides
from shared.kafka.producer import KafkaProducer
from shared.models import Ride


def main():
    ride_producer = KafkaProducer[Ride](config.kafka.bootstrap_servers, config.rides_producer.topic)
    for ride in load_rides(config.rides_producer.json_file):
        sleep(config.rides_producer.sim_speed)
        ride.timestamp = datetime.datetime.now()
        ride_producer.send(ride)


if __name__ == "__main__":
    main()
