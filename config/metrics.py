from pydantic import BaseModel

class MetricsConfig(BaseModel):
    group_id: str = "metrics"