from services.ai_service import AIService
from tasks.celery_app import celery_app


@celery_app.task(name="tasks.ai_tasks.generate_summary")
def generate_summary(body: str) -> str:
    import asyncio

    return asyncio.run(AIService().summarize_email(body))
