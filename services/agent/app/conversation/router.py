from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..api.deps import current_user
from ..db.session import get_session
from ..models.db_models import User
from ..schemas.common import (
    ConversationCreate,
    ConversationDetailResponse,
    ConversationListResponse,
    ConversationOut,
    ConversationUpdate,
    MessageOut,
)
from .service import (
    clear_messages,
    create,
    get_conversation,
    list_page,
    messages,
    runtime_summary,
    restore,
    soft_delete,
    update,
)

router = APIRouter(prefix="/conversations", tags=["conversations"])


def serialize_conversation(row):
    conversation = row["conversation"] if isinstance(row, dict) else row
    latest_run = row.get("latest_run") if isinstance(row, dict) else None
    is_running = bool(row.get("is_running")) if isinstance(row, dict) else False

    return {
        "id": conversation.id,
        "title": conversation.title,
        "agent_id": conversation.agent_id,
        "status": conversation.status,
        "is_pinned": conversation.is_pinned,
        "is_running": is_running,
        "latest_run": latest_run,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
    }


@router.get("", response_model=ConversationListResponse)
async def list_conversations(
    q: str = Query("", max_length=200),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_value: str | None = Query(None, alias="status"),
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
):
    rows, total, has_next = await list_page(
        session,
        user,
        q,
        page,
        page_size,
        status_value,
    )

    return {
        "items": [serialize_conversation(row) for row in rows],
        "page": page,
        "page_size": page_size,
        "total": total,
        "has_next": has_next,
    }


@router.post("", response_model=ConversationOut, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreate,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
):
    row = await create(session, user, payload)
    return serialize_conversation(row)


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_detail(
    conversation_id: str,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
):
    summary = await runtime_summary(session, user, conversation_id)
    items = await messages(session, user, conversation_id)
    return {
        "conversation": serialize_conversation(summary),
        "messages": items,
    }


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
async def get_messages(
    conversation_id: str,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
):
    return await messages(session, user, conversation_id)


@router.patch("/{conversation_id}", response_model=ConversationOut)
async def update_conversation(
    conversation_id: str,
    payload: ConversationUpdate,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
):
    row = await update(session, user, conversation_id, payload)
    return serialize_conversation(row)


@router.post("/{conversation_id}/archive", response_model=ConversationOut)
async def archive_conversation(
    conversation_id: str,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
):
    row = await update(
        session,
        user,
        conversation_id,
        ConversationUpdate(status="archived"),
    )
    return serialize_conversation(row)


@router.post("/{conversation_id}/restore", response_model=ConversationOut)
async def restore_conversation(
    conversation_id: str,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
):
    row = await restore(session, user, conversation_id)
    return serialize_conversation(row)


@router.post("/{conversation_id}/pin", response_model=ConversationOut)
async def pin_conversation(
    conversation_id: str,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
):
    row = await update(
        session,
        user,
        conversation_id,
        ConversationUpdate(is_pinned=True),
    )
    return serialize_conversation(row)


@router.delete("/{conversation_id}/pin", response_model=ConversationOut)
async def unpin_conversation(
    conversation_id: str,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
):
    row = await update(
        session,
        user,
        conversation_id,
        ConversationUpdate(is_pinned=False),
    )
    return serialize_conversation(row)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
):
    await soft_delete(session, user, conversation_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{conversation_id}/messages", status_code=status.HTTP_204_NO_CONTENT)
async def delete_messages(
    conversation_id: str,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
):
    await clear_messages(session, user, conversation_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
