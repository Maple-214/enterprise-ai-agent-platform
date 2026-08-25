import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..agent.graph import graph
from ..api.deps import current_user
from ..conversation.service import get_conversation
from ..db.session import get_session
from ..models.db_models import Agent, Message, Run, RunEvent, ToolExecution, User
from ..schemas.common import RunCreate, RunEventOut, RunOut
from .service import append_event, create_run, get_run, now_utc

router = APIRouter(prefix="/runs", tags=["runs"])

def sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

@router.post("/conversations/{conversation_id}", response_model=RunOut, status_code=status.HTTP_201_CREATED)
async def create_conversation_run(conversation_id: str, payload: RunCreate, user: User = Depends(current_user), session: AsyncSession = Depends(get_session)):
    conversation = await get_conversation(session, user, conversation_id)
    return await create_run(session, user, conversation, payload.content)

@router.post("/conversations/{conversation_id}/stream")
async def stream_conversation_run(conversation_id: str, payload: RunCreate, user: User = Depends(current_user), session: AsyncSession = Depends(get_session)):
    conversation = await get_conversation(session, user, conversation_id)
    run = await create_run(session, user, conversation, payload.content)
    return StreamingResponse(_execute_stream(run.id, user.id, user.tenant_id), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"})

async def _execute_stream(run_id: str, user_id: str, tenant_id: str):
    # 每个流使用独立数据库会话，避免长连接占用请求入口会话。
    from ..db.session import SessionLocal
    async with SessionLocal() as session:
        run = await session.scalar(select(Run).where(Run.id == run_id, Run.user_id == user_id, Run.tenant_id == tenant_id))
        if not run:
            yield sse({"type": "run.failed", "run_id": run_id, "conversation_id": "", "message": "执行任务不存在"})
            return
        run.status = "running"
        run.started_at = now_utc()
        await append_event(session, run, "run.started", {"run_id": run.id})
        await session.commit()
        yield sse({"type": "run.started", "run_id": run.id, "conversation_id": run.conversation_id, "trace_id": run.trace_id})
        try:
            history = (await session.scalars(select(Message).where(Message.conversation_id == run.conversation_id).order_by(Message.created_at.asc()))).all()
            agent = await session.scalar(select(Agent).where(Agent.id == run.agent_id, Agent.tenant_id == tenant_id))
            input_messages = []
            if agent and agent.system_prompt:
                input_messages.append({"role": "system", "content": agent.system_prompt})
            input_messages.extend({"role": m.role, "content": m.content} for m in history)
            result = await graph.ainvoke({"messages": input_messages, "tenant_id": tenant_id, "user_id": user_id, "tool_events": [], "citations": []})
            for event in result.get("tool_events", []):
                execution = ToolExecution(tenant_id=tenant_id, run_id=run.id, tool_name=event["name"], status="completed", arguments=event.get("arguments", {}), result=event["result"], started_at=now_utc(), completed_at=now_utc())
                session.add(execution)
                await append_event(session, run, "tool.started", {"name": event["name"]})
                yield sse({"type": "tool.started", "run_id": run.id, "conversation_id": run.conversation_id, "tool_name": event["name"]})
                await append_event(session, run, "tool.completed", event)
                yield sse({"type": "tool.completed", "run_id": run.id, "conversation_id": run.conversation_id, "tool_name": event["name"], "result": event["result"]})
            for citation in result.get("citations", []):
                await append_event(session, run, "citation.created", citation)
                yield sse({"type": "citation.created", "run_id": run.id, "conversation_id": run.conversation_id, "source": citation["source"], "score": citation["score"]})
            final_content = ""
            for message in reversed(result.get("messages", [])):
                if message.get("role") == "assistant":
                    final_content = message.get("content", "")
                    break
            final_content = final_content or "本次任务已完成。"
            session.add(Message(conversation_id=run.conversation_id, run_id=run.id, role="assistant", content=final_content))
            run.status = "completed"
            run.completed_at = now_utc()
            await append_event(session, run, "message.created", {"role": "assistant", "content": final_content})
            await append_event(session, run, "run.completed", {"run_id": run.id})
            await session.commit()
            yield sse({"type": "message.delta", "run_id": run.id, "conversation_id": run.conversation_id, "content": final_content})
            yield sse({"type": "run.completed", "run_id": run.id, "conversation_id": run.conversation_id})
        except Exception as exc:
            run.status = "failed"
            run.error_message = str(exc)
            run.completed_at = now_utc()
            await append_event(session, run, "run.failed", {"message": str(exc)})
            await session.commit()
            yield sse({"type": "run.failed", "run_id": run.id, "conversation_id": run.conversation_id, "message": "任务执行失败，请查看服务端日志。"})

@router.get("/{run_id}", response_model=RunOut)
async def get_run_detail(run_id: str, user: User = Depends(current_user), session: AsyncSession = Depends(get_session)):
    run = await get_run(session, user, run_id)
    if not run:
        raise HTTPException(404, "执行任务不存在")
    return run

@router.get("/{run_id}/events", response_model=list[RunEventOut])
async def get_run_events(run_id: str, user: User = Depends(current_user), session: AsyncSession = Depends(get_session)):
    run = await get_run(session, user, run_id)
    if not run:
        raise HTTPException(404, "执行任务不存在")
    return (await session.scalars(select(RunEvent).where(RunEvent.run_id == run.id).order_by(RunEvent.sequence.asc()))).all()

@router.post("/{run_id}/cancel", response_model=RunOut)
async def cancel_run(run_id: str, user: User = Depends(current_user), session: AsyncSession = Depends(get_session)):
    run = await get_run(session, user, run_id)
    if not run:
        raise HTTPException(404, "执行任务不存在")
    if run.status in {"completed", "failed", "cancelled"}:
        return run
    run.status = "cancelled"
    run.completed_at = now_utc()
    await append_event(session, run, "run.cancelled", {"run_id": run.id})
    await session.commit()
    await session.refresh(run)
    return run

@router.post("/{run_id}/retry", response_model=RunOut, status_code=status.HTTP_201_CREATED)
async def retry_run(run_id: str, user: User = Depends(current_user), session: AsyncSession = Depends(get_session)):
    run = await get_run(session, user, run_id)
    if not run:
        raise HTTPException(404, "执行任务不存在")
    conversation = await get_conversation(session, user, run.conversation_id)
    return await create_run(session, user, conversation, run.input_text)
