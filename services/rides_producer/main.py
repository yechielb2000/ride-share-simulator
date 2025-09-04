import datetime
import secrets
from time import sleep

from shared.config.config import config
from shared.files import load_models_from_json
from shared.kafka.producer import KafkaProducer
from shared.models import Ride


def main():
    ride_producer = KafkaProducer(config.kafka.bootstrap_servers, config.rides_producer.topic)
    for ride in load_models_from_json(config.rides_producer.json_file, "rides", Ride):
        # I do this only to simulate random requests ride time
        sleep(config.rides_producer.sim_speed)
        random_seconds  = secrets.randbelow(16) + 5 # get range 5-20
        random_delta = datetime.timedelta(seconds=random_seconds )
        ride.timestamp = datetime.datetime.now(datetime.UTC) + random_delta

        ride_producer.send(ride)


if __name__ == "__main__":
    main()
