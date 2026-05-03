import hashlib
import hmac
import secrets
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.link_click import LinkClick
from models.tracking_pixel import TrackingPixel
from models.webhook import Webhook


class TrackingService:
    def __init__(self, db: AsyncSession, secret_key: str):
        self.db = db
        self.secret_key = secret_key.encode("utf-8")

    def sign_event(self, payload: bytes) -> str:
        return hmac.new(self.secret_key, payload, hashlib.sha256).hexdigest()

    async def create_pixel(self, email_uid: str) -> TrackingPixel:
        pixel = TrackingPixel(email_uid=email_uid, pixel_id=secrets.token_urlsafe(24), opened_count=0)
        self.db.add(pixel)
        await self.db.commit()
        await self.db.refresh(pixel)
        return pixel

    async def register_open(self, pixel_id: str) -> TrackingPixel | None:
        pixel = await self.db.scalar(select(TrackingPixel).where(TrackingPixel.pixel_id == pixel_id))
        if not pixel:
            return None
        pixel.opened_count += 1
        pixel.last_opened_at = datetime.now(UTC)
        await self.db.commit()
        return pixel

    async def register_click(self, email_uid: str, url: str, ip_address: str, user_agent: str) -> LinkClick:
        click = LinkClick(email_uid=email_uid, url=url, ip_address=ip_address, user_agent=user_agent)
        self.db.add(click)
        await self.db.commit()
        await self.db.refresh(click)
        return click

    async def webhooks_for_event(self, user_id: str, event_type: str) -> list[Webhook]:
        rows = await self.db.scalars(
            select(Webhook).where(Webhook.user_id == user_id, Webhook.is_active.is_(True))
        )
        hooks = [item for item in rows if event_type in item.event_types]
        return hooks
