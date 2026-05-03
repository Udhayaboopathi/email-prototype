import base64

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db
from config import get_settings
from services.tracking_service import TrackingService

router = APIRouter(prefix="/tracking", tags=["tracking"])

TRANSPARENT_PIXEL = base64.b64decode("R0lGODlhAQABAIAAAP///////ywAAAAAAQABAAACAkQBADs=")


@router.get("/pixel/{pixel_id}", response_class=Response)
async def pixel_open(pixel_id: str, db: AsyncSession = Depends(get_db)):
    await TrackingService(db, get_settings().jwt_secret_key).register_open(pixel_id)
    return Response(content=TRANSPARENT_PIXEL, media_type="image/gif")


@router.get("/click/{email_uid}")
async def click(email_uid: str, url: str, request: Request, db: AsyncSession = Depends(get_db)):
    await TrackingService(db, get_settings().jwt_secret_key).register_click(
        email_uid=email_uid,
        url=url,
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "unknown"),
    )
    return RedirectResponse(url=url, status_code=302)
