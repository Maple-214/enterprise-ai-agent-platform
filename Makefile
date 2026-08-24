.PHONY: infra-up infra-down api worker web migrate check docker-up docker-down

infra-up:
	docker compose up -d postgres redis qdrant minio

infra-down:
	docker compose stop postgres redis qdrant minio

migrate:
	uv run --directory services/agent alembic upgrade head

api:
	uv run --directory services/agent uvicorn app.main:app --reload --port 8000

worker:
	uv run --directory services/worker python worker.py

web:
	pnpm --dir apps/web dev

check:
	python -m compileall -q services/agent services/worker
	pnpm --dir apps/web typecheck

# Full Docker mode
docker-up:
	docker compose up -d --build

docker-down:
	docker compose down
