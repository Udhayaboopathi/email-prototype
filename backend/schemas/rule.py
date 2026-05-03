from datetime import datetime

from pydantic import BaseModel


class RuleCreate(BaseModel):
    mailbox_id: str
    name: str
    conditions: dict[str, str]
    actions: dict[str, str]
    is_active: bool = True


class RuleResponse(BaseModel):
    id: str
    mailbox_id: str
    name: str
    conditions: dict[str, str]
    actions: dict[str, str]
    is_active: bool
    created_at: datetime
