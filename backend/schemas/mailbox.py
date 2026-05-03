from datetime import datetime

from pydantic import BaseModel


class MailboxCreate(BaseModel):
    user_id: str
    domain_id: str
    address: str
    quota_mb: int = 2048


class MailboxResponse(BaseModel):
    id: str
    user_id: str
    domain_id: str
    address: str
    quota_mb: int
    is_active: bool
    created_at: datetime
