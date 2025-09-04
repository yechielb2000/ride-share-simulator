from collections.abc import Generator
from typing import TypeVar

from confluent_kafka import Consumer, KafkaException
from pydantic import BaseModel

from shared.logger import logger

T = TypeVar("T", bound=BaseModel)


class KafkaConsumer:
    def __init__(self, bootstrap_servers: str, group_id: str, topic: str, model_cls: type[T]):
        """
        Initialize the Kafka consumer and subscribe it to a topic.
        
        Parameters:
            bootstrap_servers (str): Kafka bootstrap server(s) address(es) (e.g. "host:port" or comma-separated list).
            group_id (str): Consumer group id used for offset management.
            topic (str): Topic name to subscribe to.
            model_cls (type[T]): Pydantic model class used to parse message JSON payloads into instances of T.
        """
        self.consumer = Consumer({
            "bootstrap.servers": bootstrap_servers,
            "group.id": group_id,
            "auto.offset.reset": "earliest",
        })
        self.consumer.subscribe([topic])
        self.model_cls = model_cls

    def consume(self) -> Generator[T, None, None]:
        """
        Yield instances of the configured Pydantic model parsed from messages read from the Kafka topic.
        
        Continuously polls the Kafka consumer and yields objects of type T produced by calling
        model_cls.model_validate_json on each message value (decoded as UTF-8). The generator blocks
        while polling; it returns only if iteration is stopped or an unrecoverable error occurs.
        Raises KafkaException if a polled message contains an error. The underlying Kafka consumer
        is closed when the generator is exhausted or an exception escapes.
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
