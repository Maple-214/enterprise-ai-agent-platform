import asyncio
import hashlib
import math
import uuid
from pathlib import Path

import boto3
from botocore.client import Config
from pypdf import PdfReader
from qdrant_client import AsyncQdrantClient, models
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import settings

DIM = 384


def embed(text_value: str) -> list[float]:
    vector = [0.0] * DIM
    for token in text_value.lower().split():
        digest = hashlib.sha256(token.encode()).digest()
        for i in range(0, len(digest), 4):
            idx = int.from_bytes(digest[i : i + 4], "little") % DIM
            vector[idx] += 1 if digest[i] % 2 == 0 else -1
    norm = math.sqrt(sum(x * x for x in vector)) or 1
    return [x / norm for x in vector]


def storage():
    protocol = "https" if settings.minio_secure else "http"
    return boto3.client(
        "s3",
        endpoint_url=f"{protocol}://{settings.minio_endpoint}",
        aws_access_key_id=settings.minio_access_key,
        aws_secret_access_key=settings.minio_secret_key,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )


async def fetch_doc(session_factory, doc_id: str) -> bool | None:
    async with session_factory() as session:
        row = (
            await session.execute(
                text(
                    "SELECT id, tenant_id, filename, object_key, mime_type "
                    "FROM documents WHERE id=:id"
                ),
                {"id": doc_id},
            )
        ).mappings().first()

        if not row:
            return None

        data = storage().get_object(Bucket=settings.minio_bucket, Key=row["object_key"])["Body"].read()

        if row["mime_type"] == "application/pdf" or row["filename"].lower().endswith(".pdf"):
            tmp = Path("/tmp") / row["filename"]
            tmp.write_bytes(data)
            reader = PdfReader(str(tmp))
            text_content = "\n".join((page.extract_text() or "") for page in reader.pages)
        else:
            text_content = data.decode("utf-8", errors="ignore")

        chunks = [
            text_content[i : i + 900]
            for i in range(0, len(text_content), 900)
            if text_content[i : i + 900].strip()
        ]

        client = AsyncQdrantClient(url=settings.qdrant_url)
        collections = await client.get_collections()
        collection_names = [collection.name for collection in collections.collections]
        if settings.qdrant_collection not in collection_names:
            await client.create_collection(
                collection_name=settings.qdrant_collection,
                vectors_config=models.VectorParams(
                    size=DIM,
                    distance=models.Distance.COSINE,
                ),
            )

        points = [
            models.PointStruct(
                id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"{doc_id}:{i}")),
                vector=embed(chunk),
                payload={
                    "tenant_id": row["tenant_id"],
                    "document_id": doc_id,
                    "filename": row["filename"],
                    "chunk_index": i,
                    "text": chunk,
                },
            )
            for i, chunk in enumerate(chunks)
        ]

        if points:
            await client.upsert(collection_name=settings.qdrant_collection, points=points)

        await session.execute(
            text("UPDATE documents SET status='ready' WHERE id=:id"),
            {"id": doc_id},
        )
        await session.commit()
        await client.close()
        return True


async def main() -> None:
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    print(
        "Worker started. "
        f"redis={settings.redis_url} "
        f"database={settings.database_url.split('@')[-1]} "
        f"qdrant={settings.qdrant_url}",
        flush=True,
    )

    try:
        while True:
            try:
                item = await redis.blpop("agent:jobs", timeout=5)
            except Exception as exc:
                print(f"Redis unavailable: {exc}. Retrying in 2s...", flush=True)
                await asyncio.sleep(2)
                continue

            if not item:
                continue

            _, job = item
            if job.startswith("document.index:"):
                doc_id = job.split(":", 1)[1]
                try:
                    await fetch_doc(factory, doc_id)
                except Exception as exc:
                    print(f"document job failed: {doc_id}: {exc}", flush=True)
    finally:
        await redis.aclose()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
