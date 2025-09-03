import json

import redis

from shared.models import Assignment, Assignments
from shared.models.metrics import Report, Metrics


class MetricsRedisSDK:

    def __init__(self, pool: redis.ConnectionPool) -> None:
        self._pool = pool

    @property
    def client(self) -> redis.Redis:
        return redis.Redis(connection_pool=self._pool)

    def add_assignment(self, assignment: Assignment):
        """
        Add a new assignment.
        - Store assignment JSON in a hash (by ID).
        - Store ID in sorted set by timestamp for ordering.
        Atomic via MULTI/EXEC.
        """
        key_assignments = "metrics:assignments"
        key_hash = f"metrics:assignment:{assignment.id}"
        score = assignment.pickup_time.timestamp()

        pipe = self.client.pipeline(transaction=True)
        serialized_data = json.loads(assignment.model_dump_json())
        pipe.hset(key_hash, mapping=serialized_data)
        pipe.zadd(key_assignments, {assignment.id: score})
        pipe.execute()

    def list_assignments(self) -> Assignments:
        """
        Return all assignments in timestamp order.
        """
        key_assignments = "metrics:assignments"
        ids = self.client.zrange(key_assignments, 0, -1)

        assignments = Assignments()
        for rid in ids:
            raw = self.client.hgetall(f"metrics:assignment:{rid}")
            if raw:
                assignments.append(Assignment.model_validate(raw))
        return assignments

    def add_unassigned(self, ride_id: str):
        key = "metrics:unassigned"
        self.client.sadd(key, ride_id)

    def remove_unassigned(self, ride_id: str):
        key = "metrics:unassigned"
        self.client.srem(key, ride_id)

    def list_unassigned(self) -> list[str]:
        key = "metrics:unassigned"
        return [ride_id for ride_id in self.client.smembers(key)]

    def get_report(self) -> Report:
        assignments = self.list_assignments()
        unassigned = self.list_unassigned()
        avg_eta = assignments.average_pickup_time()

        return Report(
            assignments=assignments,
            unassigned_rides=unassigned,
            metrics=Metrics(avg_pickup_eta_minutes=avg_eta),
        )
