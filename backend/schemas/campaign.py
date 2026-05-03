from datetime import datetime

from pydantic import BaseModel


class CampaignCreate(BaseModel):
    name: str
    subject: str
    body_html: str
    scheduled_at: datetime | None = None


class CampaignResponse(BaseModel):
    id: str
    user_id: str
    name: str
    subject: str
    body_html: str
    status: str
    scheduled_at: datetime | None
    sent_at: datetime | None
