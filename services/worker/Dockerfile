FROM ghcr.io/astral-sh/uv:0.10.0 AS uv
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

COPY --from=uv /uv /uvx /bin/
COPY pyproject.toml ./
RUN uv sync --no-dev

COPY worker.py ./worker.py
COPY config.py ./config.py

CMD ["uv", "run", "python", "worker.py"]
