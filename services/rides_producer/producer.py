from confluent_kafka import Producer

from shared.models import Ride


class RideProducer:
    def __init__(self, bootstrap_servers: str, topic: str):
        self.producer = Producer({"bootstrap.servers": bootstrap_servers})
        self.topic = topic

    def __delivery_report(self, err, msg):
        if err is not None:
            # TODO: change to logs when we make logger it
            print(f"Delivery failed for record {msg.key()}: {err}")
        else:
            print(f"Record {msg.key()} successfully produced to {msg.topic()} [{msg.partition()}]")

    def produce_ride(self, ride: Ride):
        self.producer.produce(
            topic=self.topic,
            key=str(ride.id),
            value=ride.model_dump(),
            callback=self.__delivery_report
        )
        self.producer.flush()
