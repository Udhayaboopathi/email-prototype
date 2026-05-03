from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db
from models.contact import Contact
from schemas.contact import ContactCreate, ContactResponse

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("/", response_model=ContactResponse)
async def create_contact(payload: ContactCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    row = Contact(user_id=user.id, email=payload.email, name=payload.name, phone=payload.phone, tags=payload.tags)
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return ContactResponse(id=row.id, user_id=row.user_id, email=row.email, name=row.name, phone=row.phone, tags=row.tags, created_at=row.created_at)


@router.get("/", response_model=list[ContactResponse])
async def list_contacts(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    rows = await db.scalars(select(Contact).where(Contact.user_id == user.id))
    return [ContactResponse(id=row.id, user_id=row.user_id, email=row.email, name=row.name, phone=row.phone, tags=row.tags, created_at=row.created_at) for row in rows]
