from sqlalchemy import text
from redis.asyncio import Redis
from qdrant_client import AsyncQdrantClient

from ..core.config import settings
from ..db.session import engine
from .storage import client as storage_client


async def check_database() -> None:
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))


async def check_redis() -> None:
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    try:
        await redis.ping()
    finally:
        await redis.aclose()


async def check_qdrant() -> None:
    client = AsyncQdrantClient(url=settings.qdrant_url)
    try:
        await client.get_collections()
    finally:
        await client.close()


def check_minio() -> None:
    client = storage_client()
    client.list_buckets()
