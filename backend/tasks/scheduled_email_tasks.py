from datetime import UTC, datetime

from sqlalchemy import select

from database import SessionLocal
from models.scheduled_email import ScheduledEmail
from schemas.mail import EmailSendRequest
from services.mail_service import MailService
from tasks.celery_app import celery_app


@celery_app.task(name="tasks.scheduled_email_tasks.dispatch_due_scheduled_emails")
def dispatch_due_scheduled_emails() -> int:
    import asyncio

    async def _run() -> int:
        async with SessionLocal() as db:
            rows = await db.scalars(
                select(ScheduledEmail).where(ScheduledEmail.status == "queued", ScheduledEmail.send_at <= datetime.now(UTC))
            )
            count = 0
            for row in rows:
                await MailService().send(
                    EmailSendRequest(
                        from_email="noreply@example.com",
                        to=[row.to_email],
                        subject=row.subject,
                        body_html=row.body_html,
                        body_text=None,
                    )
                )
                row.status = "sent"
                count += 1
            await db.commit()
            return count

    return asyncio.run(_run())
