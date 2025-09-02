import redis

from shared.models import Assignment, Assignments
from shared.models.metrics import Report, Metrics


class MetricsRedisSDK:
    _client: redis.client.Redis

    def __init__(self, client: redis.client.Redis):
        self._client = client

    def add_assignment(self, assignment: Assignment):
        """
        Add a new assignment.
        - Store assignment JSON in a hash (by ID).
        - Store ID in sorted set by timestamp for ordering.
        Atomic via MULTI/EXEC.
        """
        key_assignments = "metrics:assignments"
        key_hash = f"metrics:assignment:{assignment.id}"
        score = assignment.timestamp.timestamp()

        pipe = self._client.pipeline(transaction=True)
        pipe.hset(key_hash, mapping=assignment.model_dump())
        pipe.zadd(key_assignments, {assignment.id: score})
        pipe.execute()

    def list_assignments(self) -> Assignments:
        """
        Return all assignments in timestamp order.
        """
        key_assignments = "metrics:assignments"
        ids = self._client.zrange(key_assignments, 0, -1)

        assignments = Assignments()
        for rid in ids:
            raw = self._client.hgetall(f"metrics:assignment:{rid.decode()}")
            if raw:
                decoded = {k.decode(): v.decode() for k, v in raw.items()}
                assignments.append(Assignment.model_validate(decoded))
        return assignments

    def add_unassigned(self, ride_id: str):
        key = "metrics:unassigned"
        self._client.sadd(key, ride_id)

    def remove_unassigned(self, ride_id: str):
        key = "metrics:unassigned"
        self._client.srem(key, ride_id)

    def list_unassigned(self) -> list[str]:
        key = "metrics:unassigned"
        return [r.decode() for r in self._client.smembers(key)]

    def get_report(self) -> Report:
        assignments = self.list_assignments()
        unassigned = self.list_unassigned()
        avg_eta = assignments.average_pickup_time()

        return Report(
            assignments=assignments,
            unassigned_rides=unassigned,
            metrics=Metrics(avg_pickup_eta_minutes=avg_eta),
        )
