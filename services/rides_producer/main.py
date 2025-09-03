import datetime
from time import sleep

from shared.config.config import config
from shared.files import load_models_from_json
from shared.kafka.producer import KafkaProducer
from shared.models import Ride


def main():
    ride_producer = KafkaProducer[Ride](config.kafka.bootstrap_servers, config.rides_producer.topic)
    for ride in load_models_from_json(config.rides_producer.json_file, "rides", Ride):
        sleep(config.rides_producer.sim_speed)
        ride.timestamp = datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=5)
        ride_producer.send(ride)


if __name__ == "__main__":
    main()
