import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from models.domain import Domain
from models.domain_invite import DomainInvite
from services.cloudflare_service import CloudflareService
from services.dns_guide_service import DNSGuideService


class DomainService:
    def __init__(self, db: AsyncSession):
        self.db = db
        settings = get_settings()
        self.cloudflare = CloudflareService(settings.cloudflare_api_token)
        self.dns_guide = DNSGuideService()

    async def create_domain(self, name: str, owner_user_id: str | None = None) -> Domain:
        domain = Domain(name=name.lower().strip(), is_verified=False, owner_user_id=owner_user_id)
        self.db.add(domain)
        await self.db.commit()
        await self.db.refresh(domain)
        return domain

    async def list_domains(self) -> list[Domain]:
        rows = await self.db.scalars(select(Domain))
        return list(rows)

    async def get_dns_guide(self, domain: str) -> list[dict[str, str]]:
        return self.dns_guide.records_for_domain(domain)

    async def invite_domain_admin(self, domain_id: str, email: str) -> DomainInvite:
        token = secrets.token_urlsafe(32)
        invite = DomainInvite(
            domain_id=domain_id,
            email=email.lower(),
            token=token,
            expires_at=datetime.now(UTC) + timedelta(days=2),
        )
        self.db.add(invite)
        await self.db.commit()
        await self.db.refresh(invite)
        return invite

    async def verify_domain_dns(self, domain_name: str, records: list[str]) -> bool:
        required = {f"mx:{domain_name}", f"txt:_dmarc.{domain_name}", f"txt:{domain_name}"}
        provided = {entry.lower() for entry in records}
        verified = required.issubset(provided)
        domain = await self.db.scalar(select(Domain).where(Domain.name == domain_name))
        if domain:
            domain.is_verified = verified
            await self.db.commit()
        return verified
