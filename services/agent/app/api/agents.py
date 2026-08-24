from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..api.deps import current_user
from ..db.session import get_session
from ..models.db_models import Agent, User
from ..schemas.common import AgentOut

router = APIRouter(prefix="/agents", tags=["agents"])

@router.get("", response_model=list[AgentOut])
async def list_agents(user: User = Depends(current_user), session: AsyncSession = Depends(get_session)):
    rows = (await session.scalars(select(Agent).where(Agent.tenant_id == user.tenant_id, Agent.is_active == True))).all()
    return [AgentOut.model_validate(row) for row in rows]
