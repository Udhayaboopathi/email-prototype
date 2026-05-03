from datetime import datetime

from pydantic import BaseModel


class NoteCreate(BaseModel):
    title: str
    content: str
    pinned: bool = False


class NoteResponse(BaseModel):
    id: str
    user_id: str
    title: str
    content: str
    pinned: bool
    created_at: datetime
