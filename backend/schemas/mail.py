from datetime import datetime

from pydantic import BaseModel, EmailStr


class EmailSendRequest(BaseModel):
    from_email: EmailStr
    to: list[EmailStr]
    cc: list[EmailStr] = []
    bcc: list[EmailStr] = []
    subject: str
    body_html: str
    body_text: str | None = None


class EmailItem(BaseModel):
    uid: str
    folder: str
    subject: str
    from_email: str
    to: list[str]
    date: datetime
    seen: bool
    snippet: str


class EmailThreadResponse(BaseModel):
    id: str
    subject: str
    snippet: str
    last_message_at: datetime
