from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db
from models.email_template import EmailTemplate
from schemas.template import TemplateCreate, TemplateResponse

router = APIRouter(prefix="/templates", tags=["templates"])


@router.post("/", response_model=TemplateResponse)
async def create_template(payload: TemplateCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    row = EmailTemplate(user_id=user.id, name=payload.name, subject=payload.subject, body_html=payload.body_html, body_text=payload.body_text)
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return TemplateResponse(
        id=row.id,
        user_id=row.user_id,
        name=row.name,
        subject=row.subject,
        body_html=row.body_html,
        body_text=row.body_text,
        created_at=row.created_at,
    )


@router.get("/", response_model=list[TemplateResponse])
async def list_templates(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    rows = await db.scalars(select(EmailTemplate).where(EmailTemplate.user_id == user.id))
    return [
        TemplateResponse(
            id=row.id,
            user_id=row.user_id,
            name=row.name,
            subject=row.subject,
            body_html=row.body_html,
            body_text=row.body_text,
            created_at=row.created_at,
        )
        for row in rows
    ]
