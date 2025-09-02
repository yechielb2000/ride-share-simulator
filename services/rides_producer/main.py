from time import sleep

from config.config import config
from services.rides_producer.loader import load_rides
from shared.kafka.producer import KafkaProducer
from shared.models import Ride

ride_producer = KafkaProducer[Ride](config.kafka.bootstrap_servers, config.rides_producer.topic)


def __delivery_report(err, msg):
    if err is not None:
        # TODO: change to logs when we make logger it
        print(f"Delivery failed for record {msg.key()}: {err}")
    else:
        print(f"Record {msg.key()} successfully produced to {msg.topic()} [{msg.partition()}]")


def main():
    for ride in load_rides(config.rides_producer.json_file):
        sleep(config.rides_producer.sim_speed)
        ride_producer.send(ride, callback=__delivery_report)


if __name__ == "__main__":
    main()
