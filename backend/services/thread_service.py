from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.email_thread import EmailThread


class ThreadService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_threads(self, mailbox_id: str) -> list[EmailThread]:
        rows = await self.db.scalars(select(EmailThread).where(EmailThread.mailbox_id == mailbox_id).order_by(EmailThread.last_message_at.desc()))
        return list(rows)
