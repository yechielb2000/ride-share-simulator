import uvicorn
from fastapi import FastAPI

from config.config import config
from shared.redis_sdk import redis_client

app = FastAPI()


@app.get("/report")
async def get_report():
    return redis_client.metrics.get_report()


if __name__ == '__main__':
    uvicorn.run(app, host=config.metrics.host, port=config.metrics.port)
