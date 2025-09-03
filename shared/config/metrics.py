from pydantic import BaseModel

class MetricsConfig(BaseModel):
    group_id: str = "metrics"
    host: str = "0.0.0.0"
    port: int = 8080
