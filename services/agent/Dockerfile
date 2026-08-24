FROM ghcr.io/astral-sh/uv:0.10.0 AS uv
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

COPY --from=uv /uv /uvx /bin/
COPY pyproject.toml ./
# uv.lock is intentionally generated and committed by the development team after
# the first successful `uv lock`. During the initial bootstrap, uv resolves from pyproject.toml.
RUN uv sync --no-dev

COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app

EXPOSE 8000
CMD ["sh", "-c", "uv run alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
