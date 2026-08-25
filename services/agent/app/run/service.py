import uuid
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.db_models import Agent, Conversation, Message, Run, RunEvent, User


def now_utc():
    return datetime.now(timezone.utc)

async def get_run(session: AsyncSession, user: User, run_id: str) -> Run | None:
    return await session.scalar(select(Run).where(Run.id == run_id, Run.tenant_id == user.tenant_id, Run.user_id == user.id))

async def create_run(session: AsyncSession, user: User, conversation: Conversation, content: str) -> Run:
    active_run = await session.scalar(
        select(Run.id).where(
            Run.conversation_id == conversation.id,
            Run.tenant_id == user.tenant_id,
            Run.user_id == user.id,
            Run.status.in_(["queued", "running"]),
        ).limit(1)
    )
    if active_run:
        raise HTTPException(409, "当前对话已有任务正在执行，请等待完成后再发送")

    agent = await session.scalar(select(Agent).where(Agent.id == conversation.agent_id, Agent.tenant_id == user.tenant_id, Agent.is_active.is_(True)))
    if not agent:
        raise ValueError("智能体不存在或已停用")
    run = Run(
        tenant_id=user.tenant_id,
        user_id=user.id,
        conversation_id=conversation.id,
        agent_id=agent.id,
        status="queued",
        input_text=content,
        model=agent.model,
        trace_id=str(uuid.uuid4()),
    )
    session.add(run)
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        if "uq_runs_one_active_per_conversation" in str(exc.orig):
            raise HTTPException(409, "当前对话已有任务正在执行，请等待完成后再发送") from exc
        raise

    session.add(Message(conversation_id=conversation.id, run_id=run.id, role="user", content=content))
    await append_event(session, run, "run.created", {"run_id": run.id})
    conversation.updated_at = now_utc()
    await session.commit()
    await session.refresh(run)
    return run

async def append_event(session: AsyncSession, run: Run, event_type: str, payload: dict) -> RunEvent:
    last = await session.scalar(select(RunEvent).where(RunEvent.run_id == run.id).order_by(RunEvent.sequence.desc()).limit(1))
    seq = (last.sequence + 1) if last else 1
    event = RunEvent(tenant_id=run.tenant_id, run_id=run.id, event_type=event_type, payload=payload, sequence=seq)
    session.add(event)
    await session.flush()
    return event
