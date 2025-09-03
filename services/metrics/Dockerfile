FROM ride-share-base:latest

WORKDIR /app

COPY services/metrics/ ./services/metrics
COPY services/__init__.py ./services/

CMD ["uvicorn", "services.metrics.main:app", "--host", "0.0.0.0", "--port", "8000"]
