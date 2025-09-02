FROM ghcr.io/astral-sh/uv:python3.12-alpine

ENV UV_COMPILE_BYTECODE=1
ENV UV_PROJECT_ENVIRONMENT="/usr/local"

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY shared/ ./shared
COPY config/ ./config
COPY services/rides_producer/ ./services/rides_producer

RUN uv sync --frozen --no-cache



CMD ["python", "-m", "services.rides_producer.main"]
