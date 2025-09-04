from pydantic import BaseModel, ConfigDict

from shared.models import Assignments


class Metrics(BaseModel):
    avg_pickup_eta: float = 0.0


class Report(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    assignments: Assignments = Assignments()
    unassigned_rides: list[str] = []
    metrics: Metrics = Metrics()
