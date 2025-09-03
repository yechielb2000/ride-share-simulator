FROM ride-share-base:latest

WORKDIR /app

COPY services/clock/ ./services/clock
COPY services/__init__.py ./services/

CMD ["python", "-m", "services.clock.main"]
