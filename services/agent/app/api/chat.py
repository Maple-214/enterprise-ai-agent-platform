import json
import uuid
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..agent.graph import graph
from ..api.deps import current_user
from ..db.session import get_session
from ..models.db_models import Conversation, Message, User
from ..schemas.common import ChatRequest

router = APIRouter(prefix="/chat", tags=["chat"])


def sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

@router.post("/stream")
async def chat_stream(payload: ChatRequest, user: User = Depends(current_user), session: AsyncSession = Depends(get_session)):
    conversation = await session.scalar(select(Conversation).where(Conversation.id == payload.conversation_id, Conversation.tenant_id == user.tenant_id, Conversation.user_id == user.id))
    if not conversation:
        return StreamingResponse(iter([sse({"type": "run.failed", "message": "Conversation not found"})]), media_type="text/event-stream")
    user_message = Message(conversation_id=conversation.id, role="user", content=payload.content)
    session.add(user_message)
    await session.commit()

    async def event_stream():
        run_id = str(uuid.uuid4())
        yield sse({"type": "run.started", "run_id": run_id})
        result = await graph.ainvoke({"messages": [{"role": "user", "content": payload.content}], "tenant_id": user.tenant_id, "user_id": user.id, "tool_events": [], "citations": []})
        events = result.get("tool_events", [])
        for event in events:
            yield sse({"type": "tool.started", "tool_name": event["name"]})
            yield sse({"type": "tool.completed", "tool_name": event["name"], "result": event["result"]})
        for citation in result.get("citations", []):
            yield sse({"type": "citation.created", "source": citation["source"], "score": citation["score"]})
        final_content = ""
        for message in reversed(result.get("messages", [])):
            if message.get("role") == "assistant":
                final_content = message.get("content", "")
                break
        if not final_content:
            final_content = "Agent 已执行完成。"
        yield sse({"type": "message.delta", "content": final_content})
        assistant = Message(conversation_id=conversation.id, role="assistant", content=final_content)
        session.add(assistant)
        await session.commit()
        yield sse({"type": "run.completed", "run_id": run_id})

    return StreamingResponse(event_stream(), media_type="text/event-stream", headers={"Cache-Control":"no-cache","Connection":"keep-alive","X-Accel-Buffering":"no"})
