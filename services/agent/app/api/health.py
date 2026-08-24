import asyncio

from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

from ..services.dependencies import check_database, check_minio, check_qdrant, check_redis

router = APIRouter()
REQUESTS = Counter("agent_api_health_requests_total", "Health endpoint requests")


@router.get("/health/live")
async def live():
    REQUESTS.inc()
    return {"status": "ok", "service": "enterprise-ai-agent-platform"}


@router.get("/health/ready")
async def ready():
    checks = {}
    failures = []

    async_checks = {
        "database": check_database,
        "redis": check_redis,
        "qdrant": check_qdrant,
    }
    for name, check in async_checks.items():
        try:
            await check()
            checks[name] = "ok"
        except Exception as exc:
            checks[name] = "error"
            failures.append(f"{name}: {type(exc).__name__}")

    try:
        await asyncio.to_thread(check_minio)
        checks["minio"] = "ok"
    except Exception as exc:
        checks["minio"] = "error"
        failures.append(f"minio: {type(exc).__name__}")

    payload = {"status": "ok" if not failures else "not_ready", "checks": checks}
    return JSONResponse(status_code=200 if not failures else 503, content=payload)


@router.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
