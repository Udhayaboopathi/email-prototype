from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db
from models.spam_report import SpamReport

router = APIRouter(prefix="/spam-reports", tags=["spam-reports"])


@router.post("/", response_model=dict[str, str])
async def create_report(payload: dict[str, str], db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    row = SpamReport(email_uid=payload["email_uid"], reporter_user_id=user.id, reason=payload["reason"])
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return {"id": row.id}


@router.get("/", response_model=list[dict[str, str]])
async def list_reports(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    rows = await db.scalars(select(SpamReport).where(SpamReport.reporter_user_id == user.id))
    return [{"id": row.id, "email_uid": row.email_uid, "reason": row.reason} for row in rows]
