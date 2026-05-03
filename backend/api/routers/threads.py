from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db
from schemas.mail import EmailThreadResponse
from services.thread_service import ThreadService

router = APIRouter(prefix="/threads", tags=["threads"])


@router.get("/{mailbox_id}", response_model=list[EmailThreadResponse])
async def list_threads(mailbox_id: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    threads = await ThreadService(db).list_threads(mailbox_id)
    return [EmailThreadResponse(id=t.id, subject=t.subject, snippet=t.snippet, last_message_at=t.last_message_at) for t in threads]
