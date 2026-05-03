import hashlib

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db
from models.api_key import APIKey
from schemas.mail import EmailSendRequest
from services.mail_service import MailService

router = APIRouter(prefix="/send-api", tags=["send-api"])


@router.post("/send", response_model=dict[str, str])
async def send_via_api(payload: EmailSendRequest, x_api_key: str = Header(default=""), db: AsyncSession = Depends(get_db)):
    key_hash = hashlib.sha256(x_api_key.encode("utf-8")).hexdigest()
    key = await db.scalar(select(APIKey).where(APIKey.key_hash == key_hash, APIKey.is_active.is_(True)))
    if not key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    message_id = await MailService().send(payload)
    return {"message_id": message_id}
