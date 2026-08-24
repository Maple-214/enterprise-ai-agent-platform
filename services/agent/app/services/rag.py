import uuid

from qdrant_client import AsyncQdrantClient, models
from ..core.config import settings
from .embedding import DIMENSIONS, embed

client = AsyncQdrantClient(url=settings.qdrant_url)


async def ensure_collection() -> None:
    collections = await client.get_collections()
    if settings.qdrant_collection not in [item.name for item in collections.collections]:
        await client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=models.VectorParams(size=DIMENSIONS, distance=models.Distance.COSINE),
        )


async def index_document_chunks(document_id: str, tenant_id: str, filename: str, chunks: list[str]) -> None:
    points = []
    for idx, chunk in enumerate(chunks):
        points.append(models.PointStruct(
            id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"{document_id}:{idx}")),
            vector=embed(chunk),
            payload={"tenant_id": tenant_id, "document_id": document_id, "filename": filename, "chunk_index": idx, "text": chunk},
        ))
    if points:
        await client.upsert(collection_name=settings.qdrant_collection, points=points)


async def search_knowledge(tenant_id: str, query: str, limit: int = 5) -> list[dict]:
    results = await client.query_points(
        collection_name=settings.qdrant_collection,
        query=embed(query),
        query_filter=models.Filter(must=[models.FieldCondition(key="tenant_id", match=models.MatchValue(value=tenant_id))]),
        limit=limit,
        with_payload=True,
    )
    return [
        {"source": point.payload.get("filename", "unknown"), "score": round(float(point.score), 4), "text": point.payload.get("text", "")}
        for point in results.points
    ]
