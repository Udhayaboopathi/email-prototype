from email.message import EmailMessage

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.email_rule import EmailRule


class RulesService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_rules(self, mailbox_id: str) -> list[EmailRule]:
        rows = await self.db.scalars(select(EmailRule).where(EmailRule.mailbox_id == mailbox_id))
        return list(rows)

    async def apply_rules(self, mailbox_id: str, message: EmailMessage) -> dict[str, str]:
        rules = await self.list_rules(mailbox_id)
        actions: dict[str, str] = {}
        subject = message.get("subject", "").lower()
        from_header = message.get("from", "").lower()
        for rule in rules:
            if not rule.is_active:
                continue
            cond_subject = rule.conditions.get("subject_contains", "").lower()
            cond_from = rule.conditions.get("from_contains", "").lower()
            subject_ok = cond_subject in subject if cond_subject else True
            from_ok = cond_from in from_header if cond_from else True
            if subject_ok and from_ok:
                actions.update(rule.actions)
        return actions
