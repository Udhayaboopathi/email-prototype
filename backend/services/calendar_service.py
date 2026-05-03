from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.calendar_event import CalendarEvent
from schemas.calendar import CalendarEventCreate


class CalendarService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_event(self, user_id: str, payload: CalendarEventCreate) -> CalendarEvent:
        event = CalendarEvent(
            user_id=user_id,
            title=payload.title,
            description=payload.description,
            start_at=payload.start_at,
            end_at=payload.end_at,
            location=payload.location,
        )
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def list_events(self, user_id: str) -> list[CalendarEvent]:
        rows = await self.db.scalars(select(CalendarEvent).where(CalendarEvent.user_id == user_id).order_by(CalendarEvent.start_at.asc()))
        return list(rows)
