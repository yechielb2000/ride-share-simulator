FROM ride-share-base:latest

WORKDIR /app

COPY services/drivers_loader/ ./services/drivers_loader
COPY services/__init__.py ./services/

CMD ["python", "-m", "services.drivers_loader.main"]
