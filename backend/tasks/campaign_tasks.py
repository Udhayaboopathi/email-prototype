from datetime import UTC, datetime

from sqlalchemy import select

from database import SessionLocal
from models.campaign import Campaign
from services.campaign_service import CampaignService
from services.mail_service import MailService
from tasks.celery_app import celery_app


@celery_app.task(name="tasks.campaign_tasks.dispatch_due_campaigns")
def dispatch_due_campaigns() -> int:
    import asyncio

    async def _run() -> int:
        async with SessionLocal() as db:
            rows = await db.scalars(
                select(Campaign).where(Campaign.status == "scheduled", Campaign.scheduled_at <= datetime.now(UTC))
            )
            count = 0
            service = CampaignService(db)
            for campaign in rows:
                contacts = await service.contacts(campaign.user_id)
                recipients = [c.email for c in contacts]
                if recipients:
                    await MailService().send(
                        payload=__import__("schemas.mail", fromlist=["EmailSendRequest"]).EmailSendRequest(
                            from_email="noreply@example.com",
                            to=recipients,
                            subject=campaign.subject,
                            body_html=campaign.body_html,
                        )
                    )
                await service.mark_sent(campaign.id)
                count += 1
            return count

    return asyncio.run(_run())
