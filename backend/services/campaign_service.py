from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.campaign import Campaign
from models.contact import Contact


class CampaignService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_campaign(self, user_id: str, name: str, subject: str, body_html: str, scheduled_at: datetime | None) -> Campaign:
        campaign = Campaign(user_id=user_id, name=name, subject=subject, body_html=body_html, scheduled_at=scheduled_at, status="scheduled" if scheduled_at else "draft")
        self.db.add(campaign)
        await self.db.commit()
        await self.db.refresh(campaign)
        return campaign

    async def list_campaigns(self, user_id: str) -> list[Campaign]:
        rows = await self.db.scalars(select(Campaign).where(Campaign.user_id == user_id).order_by(Campaign.created_at.desc()))
        return list(rows)

    async def mark_sent(self, campaign_id: str) -> Campaign | None:
        campaign = await self.db.get(Campaign, campaign_id)
        if not campaign:
            return None
        campaign.status = "sent"
        campaign.sent_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(campaign)
        return campaign

    async def contacts(self, user_id: str) -> list[Contact]:
        rows = await self.db.scalars(select(Contact).where(Contact.user_id == user_id))
        return list(rows)
