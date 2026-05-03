from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db, require_role
from models.shared_mailbox import SharedMailbox
from models.user import UserRole

router = APIRouter(prefix="/shared-mailboxes", tags=["shared-mailboxes"])


@router.post("/", response_model=dict[str, str])
async def create_shared_mailbox(payload: dict[str, str], db: AsyncSession = Depends(get_db), user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin))):
    row = SharedMailbox(domain_id=user.domain_id, address=payload["address"], description=payload.get("description", ""))
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return {"id": row.id, "address": row.address}


@router.get("/", response_model=list[dict[str, str]])
async def list_shared_mailboxes(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    rows = await db.scalars(select(SharedMailbox).where(SharedMailbox.domain_id == user.domain_id))
    return [{"id": row.id, "address": row.address, "description": row.description} for row in rows]
