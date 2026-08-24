from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..api.deps import current_user
from ..db.session import get_session
from ..models.db_models import Agent, Conversation, Message, User
from ..schemas.common import ConversationCreate, ConversationOut, MessageOut

router = APIRouter(prefix="/conversations", tags=["conversations"])

@router.get("", response_model=list[ConversationOut])
async def list_conversations(user: User = Depends(current_user), session: AsyncSession = Depends(get_session)):
    rows = (await session.scalars(select(Conversation).where(Conversation.tenant_id == user.tenant_id, Conversation.user_id == user.id).order_by(Conversation.updated_at.desc()))).all()
    return [ConversationOut.model_validate(row) for row in rows]

@router.post("", response_model=ConversationOut)
async def create_conversation(payload: ConversationCreate, user: User = Depends(current_user), session: AsyncSession = Depends(get_session)):
    agent = await session.scalar(select(Agent).where(Agent.id == payload.agent_id, Agent.tenant_id == user.tenant_id))
    if not agent: raise HTTPException(404, "Agent not found")
    row = Conversation(tenant_id=user.tenant_id, user_id=user.id, agent_id=agent.id, title=payload.title)
    session.add(row); await session.commit(); await session.refresh(row)
    return row

@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
async def get_messages(conversation_id: str, user: User = Depends(current_user), session: AsyncSession = Depends(get_session)):
    conversation = await session.scalar(select(Conversation).where(Conversation.id == conversation_id, Conversation.tenant_id == user.tenant_id, Conversation.user_id == user.id))
    if not conversation: raise HTTPException(404, "Conversation not found")
    rows = (await session.scalars(select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()))).all()
    return [MessageOut.model_validate(row) for row in rows]
