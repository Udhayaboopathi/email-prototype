from datetime import datetime

from pydantic import BaseModel, EmailStr


class ContactCreate(BaseModel):
    email: EmailStr
    name: str = ""
    phone: str | None = None
    tags: list[str] = []


class ContactResponse(BaseModel):
    id: str
    user_id: str
    email: EmailStr
    name: str
    phone: str | None
    tags: list[str]
    created_at: datetime
