from confluent_kafka import Consumer, KafkaException, KafkaError
from typing import Callable
import json

class AssignmentsConsumer:
    """
    Kafka consumer for assignment messages.
    """

    def __init__(self, bootstrap_servers: str, group_id: str, topic: str, on_message: Callable[[dict], None]):
        """
        :param bootstrap_servers: Kafka bootstrap servers
        :param group_id: consumer group id
        :param topic: topic to consume from
        :param on_message: callback to process each message
        """
        self.topic = topic
        self.on_message = on_message

        self.consumer = Consumer(
            {
                "bootstrap.servers": bootstrap_servers,
                "group.id": group_id,
                "auto.offset.reset": "earliest",
            }
        )

    def start(self):
        """Start consuming messages from Kafka."""
        self.consumer.subscribe([self.topic])
        print(f"Subscribed to topic: {self.topic}")

        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError:
                        continue  # End of partition
                    else:
                        raise KafkaException(msg.error())
                try:
                    data = json.loads(msg.value().decode("utf-8"))
                    self.on_message(data)
                except Exception as e:
                    print(f"Failed to process message: {e}")
        except KeyboardInterrupt:
            print("Shutting down consumer...")
        finally:
            self.consumer.close()
