from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.mailbox import Mailbox
from schemas.mailbox import MailboxCreate


class MailboxService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_mailbox(self, user_id: str, domain_id: str, address: str, quota_mb: int = 2048) -> Mailbox:
        mailbox = Mailbox(user_id=user_id, domain_id=domain_id, address=address, quota_mb=quota_mb, is_active=True)
        self.db.add(mailbox)
        await self.db.flush()
        return mailbox

    async def create_from_schema(self, payload: MailboxCreate) -> Mailbox:
        mailbox = await self.create_mailbox(payload.user_id, payload.domain_id, payload.address, payload.quota_mb)
        await self.db.commit()
        await self.db.refresh(mailbox)
        return mailbox

    async def list_by_domain(self, domain_id: str) -> list[Mailbox]:
        rows = await self.db.scalars(select(Mailbox).where(Mailbox.domain_id == domain_id))
        return list(rows)

    async def get_by_address(self, address: str) -> Mailbox | None:
        return await self.db.scalar(select(Mailbox).where(Mailbox.address == address, Mailbox.is_active.is_(True)))
