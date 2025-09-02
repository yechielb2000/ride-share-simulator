from typing import TypeVar, Generic, Generator, Type

from confluent_kafka import Consumer, KafkaException
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class KafkaConsumer(Generic[T]):
    def __init__(self, bootstrap_servers: str, group_id: str, topic: str, model_cls: Type[T]):
        self.consumer = Consumer({
            "bootstrap.servers": bootstrap_servers,
            "group.id": group_id,
            "auto.offset.reset": "earliest"
        })
        self.consumer.subscribe([topic])
        self.model_cls = model_cls

    def consume(self) -> Generator[T, None, None]:
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

                yield self.model_cls.model_validate(msg.value().decode())
        finally:
            self.consumer.close()
