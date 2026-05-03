from datetime import datetime

from pydantic import BaseModel


class LabelCreate(BaseModel):
    mailbox_id: str
    name: str
    color: str = "#3b82f6"


class LabelResponse(BaseModel):
    id: str
    mailbox_id: str
    name: str
    color: str
    created_at: datetime
