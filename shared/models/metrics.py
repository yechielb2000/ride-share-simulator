from pydantic import BaseModel

from shared.models import Assignments


class Metrics(BaseModel):
    avg_pickup_eta_minutes: float = 0.0


class Report(BaseModel):
    assignments: Assignments = Assignments()
    unassigned_rides: list[str] = []
    metrics: Metrics = Metrics()
