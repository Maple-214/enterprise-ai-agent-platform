from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from ..api.deps import current_user
from ..conversation.service import get_conversation
from ..db.session import get_session
from ..models.db_models import User
from ..run.router import _execute_stream
from ..run.service import create_run
from ..schemas.common import ChatRequest

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/stream")
async def legacy_chat_stream(payload: ChatRequest, user: User = Depends(current_user), session: AsyncSession = Depends(get_session)):
    conversation = await get_conversation(session, user, payload.conversation_id)
    run = await create_run(session, user, conversation, payload.content)
    return StreamingResponse(_execute_stream(run.id, user.id, user.tenant_id), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"})
