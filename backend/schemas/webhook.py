from datetime import datetime

from pydantic import BaseModel


class WebhookCreate(BaseModel):
    url: str
    secret: str
    event_types: list[str]


class WebhookResponse(BaseModel):
    id: str
    user_id: str
    url: str
    event_types: list[str]
    is_active: bool
    created_at: datetime
