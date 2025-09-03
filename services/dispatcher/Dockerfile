FROM ride-share-base:latest

WORKDIR /app

COPY services/dispatcher/ ./services/dispatcher
COPY services/__init__.py ./services/

CMD ["python", "-m", "services.dispatcher.main"]
