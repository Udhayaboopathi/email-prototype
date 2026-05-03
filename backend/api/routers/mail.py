from fastapi import APIRouter, Depends

from api.deps import get_current_user
from schemas.mail import EmailItem, EmailSendRequest
from services.mail_service import MailService

router = APIRouter(prefix="/mail", tags=["mail"])


@router.get("/{folder}", response_model=list[EmailItem])
async def list_mail(folder: str, user=Depends(get_current_user)):
    return await MailService().list_folder(user.email, folder.upper())


@router.post("/send", response_model=dict[str, str])
async def send_mail(payload: EmailSendRequest, user=Depends(get_current_user)):
    message_id = await MailService().send(payload)
    return {"message_id": message_id}
