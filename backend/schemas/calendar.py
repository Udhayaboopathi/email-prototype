from datetime import datetime

from pydantic import BaseModel


class CalendarEventCreate(BaseModel):
    title: str
    description: str
    start_at: datetime
    end_at: datetime
    location: str = ""


class CalendarEventResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: str
    start_at: datetime
    end_at: datetime
    location: str
