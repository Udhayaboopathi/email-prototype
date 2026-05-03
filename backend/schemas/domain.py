from datetime import datetime

from pydantic import BaseModel


class DomainCreate(BaseModel):
    name: str


class DomainResponse(BaseModel):
    id: str
    name: str
    is_verified: bool
    created_at: datetime


class InviteCreate(BaseModel):
    email: str
