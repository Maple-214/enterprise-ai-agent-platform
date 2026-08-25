import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from .api import approvals, agents, auth, chat, health, knowledge
from .conversation.router import router as conversations_router
from .run.router import router as runs_router
from .core.config import settings
from .core.security import hash_password
from .db.session import SessionLocal
from .models.db_models import Agent, Tenant, User
from .services.dependencies import check_database, check_minio, check_qdrant, check_redis
from .services.rag import ensure_collection
from .services.storage import ensure_bucket


async def _wait_for_dependencies() -> None:
    checks = [
        ("database", check_database),
        ("redis", check_redis),
        ("qdrant", check_qdrant),
    ]
    for name, check in checks:
        last_error: Exception | None = None
        for attempt in range(30):
            try:
                await check()
                break
            except Exception as exc:
                last_error = exc
                await asyncio.sleep(1)
        else:
            raise RuntimeError(f"Dependency {name} is not ready") from last_error

    last_error = None
    for _ in range(30):
        try:
            await asyncio.to_thread(check_minio)
            break
        except Exception as exc:
            last_error = exc
            await asyncio.sleep(1)
    else:
        raise RuntimeError("Dependency minio is not ready") from last_error


@asynccontextmanager
async def lifespan(app: FastAPI):
    await _wait_for_dependencies()
    await ensure_collection()
    await asyncio.to_thread(ensure_bucket)
    await bootstrap_demo()
    yield


async def bootstrap_demo() -> None:
    if not settings.demo_bootstrap:
        return
    async with SessionLocal() as session:
        user = await session.scalar(select(User).where(User.email == settings.demo_email.lower()))
        if user:
            return
        tenant = Tenant(name="Demo Enterprise")
        session.add(tenant)
        await session.flush()
        user = User(
            tenant_id=tenant.id,
            email=settings.demo_email.lower(),
            display_name="Demo Admin",
            password_hash=hash_password(settings.demo_password),
            role="owner",
        )
        agent = Agent(
            tenant_id=tenant.id,
            name="Enterprise Assistant",
            description="企业知识与工具 Agent 演示",
            system_prompt="你是一名企业级 AI 助手。优先使用企业工具和知识库。",
            enabled_tools=["calculator", "get_system_status", "knowledge_search"],
        )
        session.add_all([user, agent])
        await session.commit()


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.web_origin, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health.router)
app.include_router(auth.router, prefix="/api")
app.include_router(agents.router, prefix="/api")
app.include_router(conversations_router, prefix="/api")
app.include_router(runs_router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(knowledge.router, prefix="/api")
app.include_router(approvals.router, prefix="/api")
