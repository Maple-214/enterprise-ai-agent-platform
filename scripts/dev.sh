#!/usr/bin/env bash
set -euo pipefail

command -v docker >/dev/null
docker compose version >/dev/null
command -v uv >/dev/null
command -v node >/dev/null
command -v pnpm >/dev/null

if [[ ! -f .env ]]; then
  cp .env.example .env
fi

docker compose up -d postgres redis qdrant minio
uv sync --directory services/agent
uv sync --directory services/worker
uv run --directory services/agent alembic upgrade head

cat <<'INFO'
Development commands:
  API:    uv run --directory services/agent uvicorn app.main:app --reload --port 8000
  Worker: uv run --directory services/worker python worker.py
  Web:    pnpm --dir apps/web dev

API docs: http://localhost:8000/docs
Web:      http://localhost:5173
INFO
