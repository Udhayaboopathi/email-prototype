from datetime import UTC, datetime, timedelta

from config import get_settings
from database import SessionLocal
from models.audit_log import AuditLog
from tasks.celery_app import celery_app
from sqlalchemy import delete


@celery_app.task(name="tasks.retention_tasks.enforce_retention")
def enforce_retention() -> int:
    import asyncio

    settings = get_settings()

    async def _run() -> int:
        async with SessionLocal() as db:
            cutoff = datetime.now(UTC) - timedelta(days=settings.backup_retention_days)
            result = await db.execute(delete(AuditLog).where(AuditLog.created_at < cutoff))
            await db.commit()
            return result.rowcount or 0

    return asyncio.run(_run())
