FROM ride-share-base:latest

WORKDIR /app

COPY services/metrics/ ./services/metrics
COPY services/__init__.py ./services/

CMD ["python", "-m", "services.metrics.main"]
