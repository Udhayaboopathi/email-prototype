from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db
from models.note import Note
from schemas.note import NoteCreate, NoteResponse

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("/", response_model=NoteResponse)
async def create_note(payload: NoteCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    row = Note(user_id=user.id, title=payload.title, content=payload.content, pinned=payload.pinned)
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return NoteResponse(id=row.id, user_id=row.user_id, title=row.title, content=row.content, pinned=row.pinned, created_at=row.created_at)


@router.get("/", response_model=list[NoteResponse])
async def list_notes(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    rows = await db.scalars(select(Note).where(Note.user_id == user.id).order_by(Note.pinned.desc(), Note.updated_at.desc()))
    return [NoteResponse(id=row.id, user_id=row.user_id, title=row.title, content=row.content, pinned=row.pinned, created_at=row.created_at) for row in rows]
