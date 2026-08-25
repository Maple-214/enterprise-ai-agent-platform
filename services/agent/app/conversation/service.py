from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.db_models import (
    Agent,
    AuditLog,
    Conversation,
    Message,
    Run,
    User,
)
from ..schemas.common import ConversationUpdate


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


async def get_conversation(
    session: AsyncSession,
    user: User,
    conversation_id: str,
    include_deleted: bool = False,
) -> Conversation:
    """
    获取当前用户可访问的会话。

    默认不返回已删除的会话。
    """
    stmt = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.tenant_id == user.tenant_id,
        Conversation.user_id == user.id,
    )

    if not include_deleted:
        stmt = stmt.where(
            Conversation.deleted_at.is_(None),
        )

    conversation = await session.scalar(stmt)

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="对话不存在或无权访问",
        )

    return conversation


async def audit(
    session: AsyncSession,
    user: User,
    action: str,
    resource_id: str,
    metadata: dict | None = None,
) -> None:
    """
    写入会话审计日志。
    """
    session.add(
        AuditLog(
            tenant_id=user.tenant_id,
            user_id=user.id,
            action=action,
            resource_type="conversation",
            resource_id=resource_id,
            audit_metadata=metadata or {},
        )
    )


async def create(
    session: AsyncSession,
    user: User,
    payload,
) -> Conversation:
    """
    创建新会话。
    """
    agent = await session.scalar(
        select(Agent).where(
            Agent.id == payload.agent_id,
            Agent.tenant_id == user.tenant_id,
            Agent.is_active.is_(True),
        )
    )

    if agent is None:
        raise HTTPException(
            status_code=404,
            detail="智能体不存在或已停用",
        )

    title = (payload.title or "").strip() or "新对话"

    conversation = Conversation(
        tenant_id=user.tenant_id,
        user_id=user.id,
        agent_id=agent.id,
        title=title,
        status="active",
        is_pinned=False,
    )

    session.add(conversation)

    await session.flush()

    await audit(
        session,
        user,
        "conversation.created",
        conversation.id,
        {
            "agent_id": agent.id,
        },
    )

    await session.commit()
    await session.refresh(conversation)

    return conversation


async def list_page(
    session: AsyncSession,
    user: User,
    q: str,
    page: int,
    page_size: int,
    status_value: str | None,
):
    """
    分页查询会话列表。

    返回：
    - conversation：会话本身
    - is_running：当前是否存在 queued/running Run
    - latest_run：最近一次 Run
    """

    filters = [
        Conversation.tenant_id == user.tenant_id,
        Conversation.user_id == user.id,
        Conversation.deleted_at.is_(None),
    ]

    # 搜索
    keyword = q.strip()

    if keyword:
        filters.append(
            or_(
                Conversation.title.ilike(
                    f"%{keyword}%"
                ),
            )
        )

    # 状态筛选
    if status_value:
        if status_value not in {
            "active",
            "archived",
        }:
            raise HTTPException(
                status_code=400,
                detail="无效的对话状态",
            )

        filters.append(
            Conversation.status == status_value,
        )

    # 总数量
    total_result = await session.scalar(
        select(func.count())
        .select_from(Conversation)
        .where(*filters)
    )

    total = int(total_result or 0)

    offset = (page - 1) * page_size

    # =========================================================
    # 最近一次 Run
    #
    # 每个 Conversation 只保留最近的一条 Run。
    # =========================================================

    ranked_runs = (
        select(
            Run.id.label("run_id"),
            Run.conversation_id.label(
                "conversation_id"
            ),
            Run.status.label("run_status"),
            Run.created_at.label(
                "run_created_at"
            ),
            Run.started_at.label(
                "run_started_at"
            ),
            Run.completed_at.label(
                "run_completed_at"
            ),
            func.row_number()
            .over(
                partition_by=Run.conversation_id,
                order_by=(
                    Run.created_at.desc(),
                    Run.id.desc(),
                ),
            )
            .label("row_number"),
        )
        .where(
            Run.tenant_id == user.tenant_id,
            Run.user_id == user.id,
        )
        .subquery("ranked_runs")
    )

    latest_run = (
        select(
            ranked_runs.c.conversation_id,
            ranked_runs.c.run_id,
            ranked_runs.c.run_status,
            ranked_runs.c.run_created_at,
            ranked_runs.c.run_started_at,
            ranked_runs.c.run_completed_at,
        )
        .where(
            ranked_runs.c.row_number == 1,
        )
        .subquery("latest_run")
    )

    # =========================================================
    # 当前是否存在正在执行的 Run
    #
    # 注意：
    # Conversation.status == "active"
    # 不代表 Agent 正在运行。
    #
    # 真正的运行状态来自 Run：
    # queued / running
    # =========================================================

    active_run_exists = (
        select(Run.id)
        .where(
            Run.conversation_id
            == Conversation.id,
            Run.tenant_id == user.tenant_id,
            Run.user_id == user.id,
            Run.status.in_(
                [
                    "queued",
                    "running",
                ]
            ),
        )
        .exists()
    )

    # =========================================================
    # 最终列表查询
    #
    # 不使用：
    # for conversation, run, is_running in rows
    #
    # 因为 latest_run 是 SQL 子查询，SQLAlchemy 会把其
    # 字段作为独立列返回。
    #
    # 所以这里使用 row[0] / row[1] ...
    # 明确读取每一列，避免字段数量变化导致解包异常。
    # =========================================================

    stmt = (
        select(
            Conversation,

            latest_run.c.run_id,
            latest_run.c.run_status,
            latest_run.c.run_created_at,
            latest_run.c.run_started_at,
            latest_run.c.run_completed_at,

            active_run_exists.label(
                "is_running"
            ),
        )
        .outerjoin(
            latest_run,
            latest_run.c.conversation_id
            == Conversation.id,
        )
        .where(*filters)
        .order_by(
            Conversation.is_pinned.desc(),
            Conversation.updated_at.desc(),
        )
        .offset(offset)
        .limit(page_size)
    )

    result = await session.execute(stmt)

    rows = result.all()

    items = []

    for row in rows:
        # -----------------------------------------------------
        # 固定列结构
        #
        # row[0] = Conversation
        # row[1] = latest run id
        # row[2] = latest run status
        # row[3] = latest run created_at
        # row[4] = latest run started_at
        # row[5] = latest run completed_at
        # row[6] = 当前是否存在 queued/running Run
        # -----------------------------------------------------

        conversation = row[0]

        run_id = row[1]
        run_status = row[2]
        run_created_at = row[3]
        run_started_at = row[4]
        run_completed_at = row[5]

        is_running = bool(row[6])

        latest_run_data = None

        if run_id is not None:
            latest_run_data = {
                "id": run_id,
                "status": run_status,
                "created_at": run_created_at,
                "started_at": run_started_at,
                "completed_at": run_completed_at,
            }

        items.append(
            {
                "conversation": conversation,
                "is_running": is_running,
                "latest_run": latest_run_data,
            }
        )

    has_next = (
        offset + len(items)
    ) < total

    return (
        items,
        total,
        has_next,
    )


async def runtime_summary(
    session: AsyncSession,
    user: User,
    conversation_id: str,
) -> dict:
    """
    获取单个会话的运行态摘要。

    用于会话详情页：
    - 最近一次 Run
    - 当前是否正在执行
    """

    conversation = await get_conversation(
        session,
        user,
        conversation_id,
    )

    # 最近一次 Run
    latest_result = await session.execute(
        select(Run)
        .where(
            Run.conversation_id
            == conversation.id,
            Run.tenant_id == user.tenant_id,
            Run.user_id == user.id,
        )
        .order_by(
            Run.created_at.desc(),
            Run.id.desc(),
        )
        .limit(1)
    )

    latest_run = (
        latest_result.scalar_one_or_none()
    )

    # 当前是否正在执行
    is_running = bool(
    await session.scalar(
        select(
            select(Run.id)
            .where(
                Run.conversation_id == conversation.id,
                Run.tenant_id == user.tenant_id,
                Run.user_id == user.id,
                Run.status.in_(["queued", "running"]),
            )
            .exists()
        )
    )
)

    latest_run_data = None

    if latest_run is not None:
        latest_run_data = {
            "id": latest_run.id,
            "status": latest_run.status,
            "created_at": latest_run.created_at,
            "started_at": latest_run.started_at,
            "completed_at": latest_run.completed_at,
        }

    return {
        "conversation": conversation,
        "is_running": is_running,
        "latest_run": latest_run_data,
    }


async def messages(
    session: AsyncSession,
    user: User,
    conversation_id: str,
):
    """
    获取会话消息。
    """

    conversation = await get_conversation(
        session,
        user,
        conversation_id,
    )

    result = await session.scalars(
        select(Message)
        .where(
            Message.conversation_id
            == conversation.id
        )
        .order_by(
            Message.created_at.asc()
        )
    )

    return result.all()


async def update(
    session: AsyncSession,
    user: User,
    conversation_id: str,
    payload: ConversationUpdate,
):
    """
    更新会话。

    注意：
    这里只修改 Conversation 生命周期属性，
    不修改任何 Run 状态。
    """

    conversation = await get_conversation(
        session,
        user,
        conversation_id,
    )

    changes: dict = {}

    if payload.title is not None:
        new_title = payload.title.strip()

        if new_title:
            conversation.title = new_title
            changes["title"] = new_title

    if payload.is_pinned is not None:
        conversation.is_pinned = (
            payload.is_pinned
        )

        changes["is_pinned"] = (
            payload.is_pinned
        )

    if payload.status is not None:
        if payload.status not in {
            "active",
            "archived",
        }:
            raise HTTPException(
                status_code=400,
                detail="无效的对话状态",
            )

        conversation.status = payload.status

        changes["status"] = (
            payload.status
        )

    conversation.updated_at = now_utc()

    await audit(
        session,
        user,
        "conversation.updated",
        conversation.id,
        changes,
    )

    await session.commit()
    await session.refresh(conversation)

    return conversation


async def soft_delete(
    session: AsyncSession,
    user: User,
    conversation_id: str,
):
    """
    软删除会话。

    不删除数据库数据。
    """

    conversation = await get_conversation(
        session,
        user,
        conversation_id,
    )

    conversation.deleted_at = now_utc()

    conversation.status = "archived"

    conversation.is_pinned = False

    conversation.updated_at = now_utc()

    await audit(
        session,
        user,
        "conversation.deleted",
        conversation.id,
    )

    await session.commit()


async def restore(
    session: AsyncSession,
    user: User,
    conversation_id: str,
):
    """
    恢复已经软删除的会话。
    """

    conversation = await get_conversation(
        session,
        user,
        conversation_id,
        include_deleted=True,
    )

    conversation.deleted_at = None

    conversation.status = "active"

    conversation.updated_at = now_utc()

    await audit(
        session,
        user,
        "conversation.restored",
        conversation.id,
    )

    await session.commit()
    await session.refresh(conversation)

    return conversation


async def clear_messages(
    session: AsyncSession,
    user: User,
    conversation_id: str,
):
    """
    清空会话消息。

    注意：
    这里只清理 Message，不会删除 Conversation，
    也不会删除 Run 历史。
    """

    conversation = await get_conversation(
        session,
        user,
        conversation_id,
    )

    message_items = (
        await session.scalars(
            select(Message).where(
                Message.conversation_id
                == conversation.id
            )
        )
    ).all()

    for message in message_items:
        await session.delete(message)

    conversation.updated_at = now_utc()

    await audit(
        session,
        user,
        "conversation.messages_cleared",
        conversation.id,
        {
            "message_count": len(
                message_items
            )
        },
    )

    await session.commit()