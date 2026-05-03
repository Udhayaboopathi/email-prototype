from celery import Celery
from celery.schedules import crontab

from config import get_settings

settings = get_settings()

celery_app = Celery("mail_platform", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.timezone = "UTC"
celery_app.conf.beat_schedule = {
    "cleanup-expired-data": {"task": "tasks.cleanup.cleanup_expired", "schedule": crontab(minute="*/30")},
    "daily-backup": {"task": "tasks.backup_tasks.run_scheduled_backup", "schedule": crontab(hour=settings.backup_schedule_hour, minute=0)},
    "dispatch-campaigns": {"task": "tasks.campaign_tasks.dispatch_due_campaigns", "schedule": crontab(minute="*/5")},
    "dispatch-scheduled-mails": {"task": "tasks.scheduled_email_tasks.dispatch_due_scheduled_emails", "schedule": crontab(minute="*/2")},
    "storage-alerts": {"task": "tasks.storage_alert_tasks.check_storage_usage", "schedule": crontab(minute=15, hour="*/2")},
    "retention-enforcement": {"task": "tasks.retention_tasks.enforce_retention", "schedule": crontab(hour=3, minute=30)},
}
celery_app.autodiscover_tasks(["tasks"])
