from datetime import datetime

from pydantic import BaseModel


class TemplateCreate(BaseModel):
    name: str
    subject: str
    body_html: str
    body_text: str


class TemplateResponse(BaseModel):
    id: str
    user_id: str
    name: str
    subject: str
    body_html: str
    body_text: str
    created_at: datetime
