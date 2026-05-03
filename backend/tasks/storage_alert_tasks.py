import asyncio
from pathlib import Path

from config import get_settings
from tasks.celery_app import celery_app


@celery_app.task(name="tasks.storage_alert_tasks.check_storage_usage")
def check_storage_usage() -> dict[str, float]:
    settings = get_settings()
    base = Path(settings.maildir_base)
    used_bytes = 0
    for file in base.rglob("*"):
        if file.is_file():
            used_bytes += file.stat().st_size
    used_mb = used_bytes / (1024 * 1024)
    quota_mb = 1024 * 1024
    return {"used_mb": used_mb, "usage_percent": (used_mb / quota_mb) * 100}
