from datetime import UTC, datetime

from sqlalchemy import delete

from database import SessionLocal
from models.password_reset_token import PasswordResetToken
from models.session import Session
from tasks.celery_app import celery_app


@celery_app.task(name="tasks.cleanup.cleanup_expired")
def cleanup_expired() -> int:
    import asyncio

    async def _run() -> int:
        async with SessionLocal() as db:
            await db.execute(delete(Session).where(Session.expires_at < datetime.now(UTC)))
            result = await db.execute(delete(PasswordResetToken).where(PasswordResetToken.expires_at < datetime.now(UTC)))
            await db.commit()
            return result.rowcount or 0

    return asyncio.run(_run())
