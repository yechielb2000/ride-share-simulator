from time import sleep

from config.config import config
from services.rides_producer.loader import load_rides
from services.rides_producer.producer import RideProducer


def main():
    ride_producer = RideProducer(config.kafka.bootstrap_servers, config.rides_producer.topic)
    for ride in load_rides(config.rides_producer.json_file):
        sleep(config.rides_producer.sim_speed)
        ride_producer.produce_ride(ride)


if __name__ == "__main__":
    main()
