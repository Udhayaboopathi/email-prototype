from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "user"
    domain_id: str | None = None


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    role: str
    domain_id: str | None
    is_active: bool
    totp_enabled: bool
    created_at: datetime
