from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db
from models.email_rule import EmailRule
from models.mailbox import Mailbox
from schemas.rule import RuleCreate, RuleResponse

router = APIRouter(prefix="/rules", tags=["rules"])


@router.post("/", response_model=RuleResponse)
async def create_rule(payload: RuleCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    row = EmailRule(
        mailbox_id=payload.mailbox_id,
        name=payload.name,
        conditions=payload.conditions,
        actions=payload.actions,
        is_active=payload.is_active,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return RuleResponse(
        id=row.id,
        mailbox_id=row.mailbox_id,
        name=row.name,
        conditions=row.conditions,
        actions=row.actions,
        is_active=row.is_active,
        created_at=row.created_at,
    )


@router.get("/{mailbox_id}", response_model=list[RuleResponse])
async def list_rules(mailbox_id: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    rows = await db.scalars(select(EmailRule).where(EmailRule.mailbox_id == mailbox_id))
    return [
        RuleResponse(
            id=row.id,
            mailbox_id=row.mailbox_id,
            name=row.name,
            conditions=row.conditions,
            actions=row.actions,
            is_active=row.is_active,
            created_at=row.created_at,
        )
        for row in rows
    ]


@router.get("/", response_model=list[RuleResponse])
async def list_my_rules(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    mailbox_ids = list(await db.scalars(select(Mailbox.id).where(Mailbox.user_id == user.id)))
    if not mailbox_ids:
        return []
    rows = await db.scalars(select(EmailRule).where(EmailRule.mailbox_id.in_(mailbox_ids)))
    return [
        RuleResponse(
            id=row.id,
            mailbox_id=row.mailbox_id,
            name=row.name,
            conditions=row.conditions,
            actions=row.actions,
            is_active=row.is_active,
            created_at=row.created_at,
        )
        for row in rows
    ]
