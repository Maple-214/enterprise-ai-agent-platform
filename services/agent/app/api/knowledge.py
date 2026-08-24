import uuid
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..api.deps import current_user
from ..core.config import settings
from ..db.session import get_session
from ..models.db_models import Document, User
from ..schemas.common import DocumentOut
from ..services.storage import ensure_bucket, put_object
from redis.asyncio import Redis

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

@router.get("/documents", response_model=list[DocumentOut])
async def list_documents(user: User = Depends(current_user), session: AsyncSession = Depends(get_session)):
    rows = (await session.scalars(select(Document).where(Document.tenant_id == user.tenant_id).order_by(Document.created_at.desc()))).all()
    return [DocumentOut.model_validate(row) for row in rows]

@router.post("/documents", response_model=DocumentOut)
async def upload_document(file: UploadFile = File(...), user: User = Depends(current_user), session: AsyncSession = Depends(get_session)):
    data = await file.read()
    ensure_bucket()
    document_id = str(uuid.uuid4())
    object_key = f"{user.tenant_id}/{document_id}/{file.filename}"
    put_object(object_key, data, file.content_type or "application/octet-stream")
    doc = Document(tenant_id=user.tenant_id, filename=file.filename, object_key=object_key, status="queued", mime_type=file.content_type or "application/octet-stream")
    session.add(doc); await session.commit(); await session.refresh(doc)
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    await redis.lpush("agent:jobs", f'document.index:{doc.id}')
    await redis.aclose()
    return doc
