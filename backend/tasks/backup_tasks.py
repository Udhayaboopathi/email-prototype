from sqlalchemy import select

from config import get_settings
from database import SessionLocal
from models.domain import Domain
from services.backup_service import BackupService
from tasks.celery_app import celery_app


@celery_app.task(name="tasks.backup_tasks.run_scheduled_backup")
def run_scheduled_backup() -> int:
    import asyncio

    settings = get_settings()

    async def _run() -> int:
        async with SessionLocal() as db:
            rows = await db.scalars(select(Domain))
            count = 0
            for domain in rows:
                await BackupService(db, settings.maildir_base, "/var/backups/mail").create_backup(domain.id)
                count += 1
            return count

    return asyncio.run(_run())
