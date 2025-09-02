import asyncio
from confluent_kafka import Consumer, KafkaException
from typing import AsyncGenerator, TypeVar, Generic

T = TypeVar("T")

class KafkaAsyncConsumer(Generic[T]):
    def __init__(self, bootstrap_servers: str, group_id: str, topic: str, model_cls):
        self.consumer = Consumer({
            "bootstrap.servers": bootstrap_servers,
            "group.id": group_id,
            "auto.offset.reset": "earliest"
        })
        self.consumer.subscribe([topic])
        self.model_cls = model_cls

    async def consume(self) -> AsyncGenerator[T, None]:
        try:
            while True:
                msg = await asyncio.to_thread(self.consumer.poll, 1.0)
                if msg is None:
                    await asyncio.sleep(0.01)
                    continue
                if msg.error():
                    raise KafkaException(msg.error())
                yield self.model_cls.load_model(msg.value().decode())
        finally:
            await asyncio.to_thread(self.consumer.close)
