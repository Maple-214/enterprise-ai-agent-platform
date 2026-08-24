$ErrorActionPreference = "Stop"

Write-Host "[1/5] Checking required tools..."
docker --version | Out-Null
docker compose version | Out-Null
uv --version | Out-Null
node --version | Out-Null
pnpm --version | Out-Null

if (-not (Test-Path ".env")) {
  Write-Host "[2/5] Creating .env from .env.example..."
  Copy-Item .env.example .env
} else {
  Write-Host "[2/5] .env already exists."
}

Write-Host "[3/5] Starting infrastructure..."
docker compose up -d postgres redis qdrant minio

Write-Host "[4/5] Syncing Python dependencies and running migrations..."
uv sync --directory services/agent
uv sync --directory services/worker
uv run --directory services/agent alembic upgrade head

Write-Host "[5/5] Development commands"
Write-Host "API:    uv run --directory services/agent uvicorn app.main:app --reload --port 8000"
Write-Host "Worker: uv run --directory services/worker python worker.py"
Write-Host "Web:    pnpm --dir apps/web dev"
Write-Host "API docs: http://localhost:8000/docs"
Write-Host "Web:      http://localhost:5173"
