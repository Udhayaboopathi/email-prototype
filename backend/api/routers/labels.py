from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db
from models.label import Label
from models.mailbox import Mailbox
from schemas.label import LabelCreate, LabelResponse

router = APIRouter(prefix="/labels", tags=["labels"])


@router.post("/", response_model=LabelResponse)
async def create_label(payload: LabelCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    label = Label(mailbox_id=payload.mailbox_id, name=payload.name, color=payload.color)
    db.add(label)
    await db.commit()
    await db.refresh(label)
    return LabelResponse(id=label.id, mailbox_id=label.mailbox_id, name=label.name, color=label.color, created_at=label.created_at)


@router.get("/{mailbox_id}", response_model=list[LabelResponse])
async def list_labels(mailbox_id: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    rows = await db.scalars(select(Label).where(Label.mailbox_id == mailbox_id))
    return [LabelResponse(id=row.id, mailbox_id=row.mailbox_id, name=row.name, color=row.color, created_at=row.created_at) for row in rows]


@router.get("/", response_model=list[LabelResponse])
async def list_my_labels(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    mailbox_ids = list(await db.scalars(select(Mailbox.id).where(Mailbox.user_id == user.id)))
    if not mailbox_ids:
        return []
    rows = await db.scalars(select(Label).where(Label.mailbox_id.in_(mailbox_ids)))
    return [LabelResponse(id=row.id, mailbox_id=row.mailbox_id, name=row.name, color=row.color, created_at=row.created_at) for row in rows]
