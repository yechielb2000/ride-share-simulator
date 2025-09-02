import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from config.config import config
from shared.kafka import KafkaAsyncConsumer
from shared.models import Assignment
from shared.models.metrics import Report


@asynccontextmanager
async def lifespan(a: FastAPI):
    asyncio.create_task(consume_assignments())
    yield


app = FastAPI(lifespan=lifespan)
report = Report()

assigment_consumer = KafkaAsyncConsumer[Assignment](
    bootstrap_servers=config.kafka.bootstrap_servers,
    group_id=config.metrics.group_id,
    topic=config.dispatcher.producer.topic,
    model_cls=Assignment
)


async def consume_assignments():
    async for assignment in assigment_consumer.consume():
        report.add_assignment(assignment)


@app.get("/report")
async def get_report():
    return report.model_dump()
