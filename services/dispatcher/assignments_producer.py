from confluent_kafka import Producer

from shared.models import Assignment


class AssignmentProducer:
    def __init__(self, bootstrap_servers: str, topic: str):
        self.producer = Producer({"bootstrap.servers": bootstrap_servers})
        self.topic = topic

    def send(self, assignment: Assignment):
        self.producer.produce(self.topic, assignment.model_dump_json())
        self.producer.flush()
