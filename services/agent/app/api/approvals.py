from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..api.deps import current_user
from ..db.session import get_session
from ..models.db_models import Approval, User
from ..schemas.common import ApprovalOut, ApprovalResolve

router = APIRouter(prefix="/approvals", tags=["approvals"])

@router.get("", response_model=list[ApprovalOut])
async def list_approvals(user: User = Depends(current_user), session: AsyncSession = Depends(get_session)):
    rows = (await session.scalars(select(Approval).where(Approval.tenant_id == user.tenant_id).order_by(Approval.created_at.desc()))).all()
    return [ApprovalOut.model_validate(row) for row in rows]

@router.post("/{approval_id}/resolve")
async def resolve_approval(approval_id: str, payload: ApprovalResolve, user: User = Depends(current_user), session: AsyncSession = Depends(get_session)):
    approval = await session.scalar(select(Approval).where(Approval.id == approval_id, Approval.tenant_id == user.tenant_id))
    if not approval: raise HTTPException(404, "Approval not found")
    if payload.decision not in {"approve", "reject"}: raise HTTPException(400, "Invalid decision")
    approval.status = "approved" if payload.decision == "approve" else "rejected"
    await session.commit()
    return {"id": approval.id, "status": approval.status}
