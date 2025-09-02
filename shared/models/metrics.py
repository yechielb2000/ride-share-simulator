from pydantic import BaseModel

from shared.models import Assignment


class Metrics(BaseModel):
    avg_pickup_eta_minutes: float = 0.0


class Report(BaseModel):
    assignments: list[Assignment] = []
    unassigned_rides: list[str] = []
    metrics: Metrics = Metrics()
