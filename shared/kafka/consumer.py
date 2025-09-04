from collections.abc import Generator

from confluent_kafka import Consumer, KafkaException
from pydantic import BaseModel

from shared.logger import logger


class KafkaConsumer:
    def __init__(self, bootstrap_servers: str, group_id: str, topic: str, model_cls: BaseModel):
        self.consumer = Consumer({
            "bootstrap.servers": bootstrap_servers,
            "group.id": group_id,
            "auto.offset.reset": "earliest",
        })
        self.consumer.subscribe([topic])
        self.model_cls = model_cls

    def consume(self) -> Generator[BaseModel, None, None]:
        """
        Continuously yield Pydantic model objects of type T from Kafka.
        """
        try:
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    raise KafkaException(msg.error())
                consumed_message_value = msg.value().decode()
                logger.debug("Consumed record", message=consumed_message_value)
                yield self.model_cls.model_validate_json(consumed_message_value)
        finally:
            self.consumer.close()
