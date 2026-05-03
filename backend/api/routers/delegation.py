from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db
from models.delegation import Delegation

router = APIRouter(prefix="/delegation", tags=["delegation"])


@router.post("/", response_model=dict[str, str])
async def grant(payload: dict[str, str], db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    row = Delegation(shared_mailbox_id=payload["shared_mailbox_id"], user_id=payload["user_id"], can_send=True, can_read=True, can_manage=False)
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return {"id": row.id}


@router.get("/mine", response_model=list[dict[str, str | bool]])
async def my_delegations(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    rows = await db.scalars(select(Delegation).where(Delegation.user_id == user.id))
    return [
        {"id": row.id, "shared_mailbox_id": row.shared_mailbox_id, "can_send": row.can_send, "can_read": row.can_read, "can_manage": row.can_manage}
        for row in rows
    ]
