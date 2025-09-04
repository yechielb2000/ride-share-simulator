from pydantic import BaseModel


class MetricsConfig(BaseModel):
    group_id: str = "metrics"
    host: str = "127.0.0.1"
    port: int = 8000
