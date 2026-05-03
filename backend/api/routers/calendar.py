from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db
from schemas.calendar import CalendarEventCreate, CalendarEventResponse
from services.calendar_service import CalendarService

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.post("/", response_model=CalendarEventResponse)
async def create_event(payload: CalendarEventCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    event = await CalendarService(db).create_event(user.id, payload)
    return CalendarEventResponse(
        id=event.id,
        user_id=event.user_id,
        title=event.title,
        description=event.description,
        start_at=event.start_at,
        end_at=event.end_at,
        location=event.location,
    )


@router.get("/", response_model=list[CalendarEventResponse])
async def list_events(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    rows = await CalendarService(db).list_events(user.id)
    return [
        CalendarEventResponse(
            id=row.id,
            user_id=row.user_id,
            title=row.title,
            description=row.description,
            start_at=row.start_at,
            end_at=row.end_at,
            location=row.location,
        )
        for row in rows
    ]
