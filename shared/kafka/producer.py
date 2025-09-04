from collections.abc import Callable

from confluent_kafka import Producer
from pydantic import BaseModel

from shared.logger import logger


class KafkaProducer:
    def __init__(self, bootstrap_servers: str, topic: str):
        self.producer = Producer({"bootstrap.servers": bootstrap_servers})
        self.topic = topic

    def send(self, item: BaseModel, callback: Callable | None = None):
        """
        Produce a generic Pydantic model to Kafka.
        """
        self.producer.produce(
            topic=self.topic,
            value=item.model_dump_json(),
            callback=callback or self.__delivery_report,
        )
        self.producer.flush()

    @staticmethod
    def __delivery_report(err, msg):
        if err is not None:
            logger.error("Delivery failed for record", exc_info=err, key=msg.key())
        else:
            logger.debug("Record delivered", key=msg.key(), topic=msg.topic(), partition=msg.partition())
