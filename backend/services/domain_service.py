"""Domain service – handles domain creation, admin provisioning, and DNS setup."""
from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta
from typing import Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from core.security import hash_password
from models.domain import Domain
from models.domain_invite import DomainInvite
from models.user import User, UserRole
from services.cloudflare_service import CloudflareService
from services.dns_guide_service import DNSGuideService
from smtp.dkim import generate_dkim_keypair, save_dkim_private_key


class DomainService:
    def __init__(self, db: AsyncSession):
        self.db = db
        settings = get_settings()
        self.settings = settings
        self.cloudflare = CloudflareService(settings.cloudflare_api_token)
        self.dns_guide = DNSGuideService()

    # ─── Core creation ────────────────────────────────────────────────────────

    async def create_domain_full(
        self,
        *,
        name: str,
        admin_email: str,
        admin_password: str,
        owner_user_id: str | None = None,
        storage_quota_mb: int | None = None,
        dns_mode: Literal["auto", "manual"] = "manual",
        cloudflare_token: str | None = None,
    ) -> tuple[Domain, User, list[dict[str, str]] | None]:
        """
        Full domain onboarding in one transaction:
          1. Create the Domain row.
          2. Create/find the domain admin User account.
          3. If dns_mode='auto', call Cloudflare to set up DNS records.
          4. Return (domain, admin_user, dns_guide_records | None).
        """
        domain_name = name.lower().strip()

        # 1 ── Create domain row ────────────────────────────────────────────
        domain = Domain(
            name=domain_name,
            is_verified=False,
            is_suspended=False,
            owner_user_id=owner_user_id,
            storage_quota_mb=storage_quota_mb,
        )
        self.db.add(domain)
        await self.db.flush()  # get domain.id without committing yet

        # 2 ── Create domain admin user ────────────────────────────────────
        existing_user = await self.db.scalar(select(User).where(User.email == admin_email.lower()))
        if existing_user:
            # Assign the existing user as domain admin for this domain
            existing_user.role = UserRole.domain_admin
            existing_user.domain_id = domain.id
            admin_user = existing_user
        else:
            admin_user = User(
                email=admin_email.lower(),
                password_hash=hash_password(admin_password),
                role=UserRole.domain_admin,
                domain_id=domain.id,
                is_active=True,
            )
            self.db.add(admin_user)

        domain.owner_user_id = admin_user.id if not existing_user else existing_user.id

        # 3 ── Generate per-domain DKIM key pair ─────────────────────────────
        private_pem, pub_b64, dkim_txt_value = generate_dkim_keypair(domain_name)
        save_dkim_private_key(domain_name, private_pem)
        domain.dkim_public_key = pub_b64  # store public key in DB

        # 4 ── DNS setup ───────────────────────────────────────────────────
        dns_records: list[dict[str, str]] | None = None
        cloudflare_error: str | None = None

        if dns_mode == "auto" and cloudflare_token:
            try:
                zone_id = await self.cloudflare.setup_email_dns(
                    domain=domain_name,
                    smtp_hostname=self.settings.smtp_hostname,
                    dkim_selector=self.settings.dkim_selector,
                    dkim_txt_value=dkim_txt_value,
                    token=cloudflare_token,
                )
                domain.cloudflare_zone_id = zone_id
                domain.is_verified = True  # DNS is auto-configured → mark verified
            except Exception as exc:
                # Don't fail the whole request; surface the error as a warning
                cloudflare_error = str(exc)
        else:
            # Return the manual DNS guide (includes the freshly generated DKIM record)
            dns_records = self.dns_guide.records_for_domain(domain_name, dkim_txt_value=dkim_txt_value)

        await self.db.commit()
        await self.db.refresh(domain)
        if not existing_user:
            await self.db.refresh(admin_user)

        return domain, admin_user, dns_records, cloudflare_error

    # ─── Legacy helpers (kept for backward compat) ───────────────────────────

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
