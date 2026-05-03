from datetime import datetime

from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    due_at: datetime | None = None


class TaskResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: str
    due_at: datetime | None
    completed: bool
