from datetime import datetime

from pydantic import BaseModel


class APIKeyCreate(BaseModel):
    name: str


class APIKeyResponse(BaseModel):
    id: str
    user_id: str
    name: str
    is_active: bool
    created_at: datetime
