from confluent_kafka import Consumer, KafkaException

from shared.models import Ride


class RidesConsumer:
    def __init__(self, bootstrap_servers: str, group_id: str, topic: str):
        self.consumer = Consumer({
            "bootstrap.servers": bootstrap_servers,
            "group.id": group_id,
            "auto.offset.reset": "earliest"
        })
        self.consumer.subscribe([topic])

    def consume(self):
        """
        yield Ride objects.
        """
        try:
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    raise KafkaException(msg.error())

                yield Ride.load_model(msg.value().decode())
        finally:
            self.consumer.close()
