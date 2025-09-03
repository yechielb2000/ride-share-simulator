FROM ride-share-base:latest

WORKDIR /app

COPY services/rides_producer/ ./services/rides_producer
COPY services/__init__.py ./services/

CMD ["python", "-m", "services.rides_producer.main"]
