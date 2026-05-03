from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db, require_role, get_current_domain_admin
from services.mailbox_service import MailboxService
from config import get_settings
import mailbox as py_mailbox
import asyncio
from core.security import hash_password
from models.audit_log import AuditLog
from models.domain import Domain
from models.ediscovery_export import EDiscoveryExport
from models.mailbox import Mailbox
from models.shared_mailbox import SharedMailbox
from models.user import User, UserRole
from schemas.domain import DomainResponse, InviteCreate
from schemas.domain_admin import MailboxCreate
from services.backup_service import create_domain_backup
from services.domain_service import DomainService
from services.dns_guide_service import DNSGuideService
from services.email_service import send_domain_admin_invite
import dns.resolver
import dns.reversename
from datetime import datetime as _dt

router = APIRouter(prefix="/domain-admin", tags=["domain-admin"])


# ─── Domain info ──────────────────────────────────────────────────────────────

@router.get("/domain", response_model=DomainResponse)
async def my_domain(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_domain_admin),
):
    domain = await db.scalar(select(Domain).where(Domain.id == user.domain_id))
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    return DomainResponse(
        id=domain.id,
        name=domain.name,
        is_verified=domain.is_verified,
        is_suspended=getattr(domain, "is_suspended", False),
        storage_quota_mb=getattr(domain, "storage_quota_mb", None),
        cloudflare_zone_id=getattr(domain, "cloudflare_zone_id", None),
        created_at=domain.created_at,
    )


@router.get("/me")
async def me(user=Depends(get_current_user)):
    return {"email": user.email, "role": user.role.value, "domain_id": user.domain_id}


# ─── Stats ────────────────────────────────────────────────────────────────────

@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_domain_admin),
):
    domain_id = user.domain_id
    total_mailboxes = await db.scalar(
        select(func.count()).select_from(Mailbox).where(Mailbox.domain_id == domain_id)
    )
    active_mailboxes = await db.scalar(
        select(func.count()).select_from(Mailbox).where(
            Mailbox.domain_id == domain_id, Mailbox.is_active.is_(True)
        )
    )
    domain = await db.scalar(select(Domain).where(Domain.id == domain_id))
    return {
        "total_mailboxes": total_mailboxes or 0,
        "active_mailboxes": active_mailboxes or 0,
        "storage_used_gb": 0,
        "storage_quota_gb": 10,
        "dns_verified": domain.is_verified if domain else False,
        "domain_name": domain.name if domain else "",
        "has_mailboxes": (total_mailboxes or 0) > 0,
        "onboarding_complete": (total_mailboxes or 0) > 0 and (domain.is_verified if domain else False),
    }


# ─── DNS Records ──────────────────────────────────────────────────────────────

@router.get("/dns-records")
@router.get("/dns-guide")
async def dns_records(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_domain_admin),
):
    domain = await db.scalar(select(Domain).where(Domain.id == user.domain_id))
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    domain_name = domain.name
    # Use DNSGuideService to produce expected records
    guide = DNSGuideService()
    return {"records": guide.records_for_domain(domain_name)}



def _resolve_txt(name: str) -> list[str]:
    try:
        answers = dns.resolver.resolve(name, "TXT", lifetime=5)
        return [b"".join(r.strings).decode() if hasattr(r, "strings") else str(r) for r in answers]
    except Exception:
        return []


def _resolve_a(name: str) -> list[str]:
    try:
        answers = dns.resolver.resolve(name, "A", lifetime=5)
        return [str(r.address) for r in answers]
    except Exception:
        return []


def _resolve_mx(name: str) -> list[str]:
    try:
        answers = dns.resolver.resolve(name, "MX", lifetime=5)
        return [str(r.exchange).rstrip(".") for r in answers]
    except Exception:
        return []


@router.get("/dns/status")
async def dns_status(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_domain_admin),
):
    domain = getattr(user, "domain", None) or await db.scalar(select(Domain).where(Domain.id == user.domain_id))
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    domain_name = domain.name
    settings = get_settings()
    server_ip = settings.server_ip

    expected_mx = f"mail.{domain_name}"
    expected_a = f"mail.{domain_name}"
    expected_spf = f"v=spf1 mx a:{domain_name} ~all"
    selector = settings.dkim_selector
    expected_dkim_name = f"{selector}._domainkey.{domain_name}"
    expected_dmarc = f"v=DMARC1; p=quarantine; rua=mailto:admin@{domain_name}"

    actual_mx = _resolve_mx(domain_name)
    actual_a = _resolve_a(expected_a)
    actual_spf = _resolve_txt(domain_name)
    actual_dkim = _resolve_txt(expected_dkim_name)
    actual_dmarc = _resolve_txt(f"_dmarc.{domain_name}")

    # PTR: reverse lookup of server_ip
    try:
        rev = dns.reversename.from_address(server_ip)
        ptr_answers = dns.resolver.resolve(rev, "PTR", lifetime=5)
        actual_ptr = [str(r.target).rstrip(".") for r in ptr_answers]
    except Exception:
        actual_ptr = []

    records = {
        "mx": {"expected": expected_mx, "actual": ",".join(actual_mx) if actual_mx else None, "valid": expected_mx in actual_mx},
        "a": {"expected": expected_a, "actual": ",".join(actual_a) if actual_a else None, "valid": server_ip in actual_a},
        "spf": {"expected": expected_spf, "actual": ",".join(actual_spf) if actual_spf else None, "valid": any(expected_spf in s for s in actual_spf)},
        "dkim": {"expected": getattr(domain, "dkim_public_key", ""), "actual": ",".join(actual_dkim) if actual_dkim else None, "valid": any(getattr(domain, "dkim_public_key", "") in s for s in actual_dkim) if getattr(domain, "dkim_public_key", None) else False},
        "dmarc": {"expected": expected_dmarc, "actual": ",".join(actual_dmarc) if actual_dmarc else None, "valid": any("v=DMARC1" in s for s in actual_dmarc)},
        "ptr": {"expected": f"mail.{domain_name}", "actual": ",".join(actual_ptr) if actual_ptr else None, "valid": any(f"mail.{domain_name}" in p for p in actual_ptr)},
    }

    all_valid = all(r["valid"] for r in records.values())

    dns_verified_at = getattr(domain, "dns_verified_at", None)
    return {
        "domain_name": domain_name,
        "server_ip": server_ip,
        "records": records,
        "all_valid": all_valid,
        "last_checked": dns_verified_at,
    }


@router.post("/dns/verify")
async def dns_verify(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_domain_admin),
):
    status = await dns_status(db=db, user=user)
    domain = getattr(user, "domain", None) or await db.scalar(select(Domain).where(Domain.id == user.domain_id))
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    if status.get("all_valid"):
        setattr(domain, "is_verified", True)
        setattr(domain, "dns_verified_at", _dt.now())
        await db.commit()
    return status


@router.post("/dns/auto")
async def dns_auto(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_domain_admin),
):
    domain = getattr(user, "domain", None) or await db.scalar(select(Domain).where(Domain.id == user.domain_id))
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    token = getattr(domain, "cloudflare_token_encrypted", None) or getattr(domain, "cloudflare_api_token", None)
    if not token:
        raise HTTPException(status_code=400, detail="No Cloudflare token configured for domain")
    # If token is encrypted, assume it's stored plaintext for now
    cf = CloudflareService(token)  # type: ignore[name-defined]
    # Attempt to find zone
    zones = await cf.list_zones()
    zone = next((z for z in zones if z.get("name") == domain.name), None)
    if not zone:
        raise HTTPException(status_code=404, detail="Cloudflare zone not found for domain")
    zone_id = zone.get("id")
    guide = DNSGuideService()
    records = guide.records_for_domain(domain.name)
    results = []
    for rec in records:
        try:
            resp = await cf.create_dns_record(zone_id, rec["type"], rec["name"], rec["value"], proxied=False)
            results.append({"record": rec, "result": resp})
        except Exception as exc:
            results.append({"record": rec, "error": str(exc)})
    return {"success": True, "records_created": len([r for r in results if "result" in r]), "errors": [r for r in results if "error" in r], "details": results}


# ─── Mailboxes ────────────────────────────────────────────────────────────────

@router.get("/mailboxes")
async def list_mailboxes(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_domain_admin),
):
    rows = list(
        await db.scalars(
            select(Mailbox).where(Mailbox.domain_id == user.domain_id).order_by(Mailbox.address)
        )
    )
    return [
        {
            "id": row.id,
            "email": row.address,
            "quota_mb": row.quota_mb,
            "is_active": row.is_active,
            "created_at": str(row.created_at) if hasattr(row, "created_at") else None,
        }
        for row in rows
    ]


@router.post("/mailboxes")
async def create_mailbox(
    payload: "MailboxCreate",
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_domain_admin),
):
    # payload validated by Pydantic
    domain = getattr(user, "domain", None) or await db.scalar(select(Domain).where(Domain.id == user.domain_id))
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    local_part = payload.local_part.strip().lower()
    password = payload.password
    quota_mb = int(payload.quota_mb or 1024)

    email_address = f"{local_part}@{domain.name}"

    # Check if mailbox already exists
    existing = await db.scalar(select(Mailbox).where(Mailbox.address == email_address))
    if existing:
        raise HTTPException(status_code=409, detail="Mailbox already exists")

    # Calculate remaining domain quota (GB -> MB). Use domain.storage_quota_gb if present, else default 10GB
    domain_quota_gb = int(getattr(domain, "storage_quota_gb", 10))
    used_sum = await db.scalar(select(func.coalesce(func.sum(Mailbox.quota_mb), 0)).where(Mailbox.domain_id == domain.id))
    used_sum = int(used_sum or 0)
    remaining_mb = domain_quota_gb * 1024 - used_sum
    if quota_mb > remaining_mb:
        raise HTTPException(status_code=422, detail="Requested quota exceeds remaining domain quota")

    # Create user account for mailbox
    mailbox_user = User(
        email=email_address,
        password_hash=hash_password(password),
        role=UserRole.user,
        domain_id=user.domain_id,
        is_active=True,
    )
    db.add(mailbox_user)
    await db.flush()

    # Create mailbox record via service
    mb_service = MailboxService(db)
    mailbox = await mb_service.create_mailbox(mailbox_user.id, user.domain_id, email_address, quota_mb)
    await db.commit()
    await db.refresh(mailbox)

    # Provision maildir on disk (create Maildir folder)
    maildir_base = get_settings().maildir_base

    async def _ensure_maildir():
        def _create():
            path = f"{maildir_base}/{domain.name}/{local_part}"
            py_mailbox.Maildir(path, create=True)

        await asyncio.to_thread(_create)

    await _ensure_maildir()

    # Log audit entry
    try:
        db.add(AuditLog(user_id=user.id, action="create_mailbox", target=email_address, ip_address="0.0.0.0", extra={}))
        await db.commit()
    except Exception:
        await db.rollback()

    return {
        "id": mailbox.id,
        "email": mailbox.address,
        "quota_mb": mailbox.quota_mb,
        "is_active": mailbox.is_active,
        "import_options": {"mbox_url": None, "zip_url": None},
    }


@router.patch("/mailboxes/{mailbox_id}")
async def update_mailbox(
    mailbox_id: str,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_domain_admin),
):
    mailbox = await db.scalar(
        select(Mailbox).where(Mailbox.id == mailbox_id, Mailbox.domain_id == user.domain_id)
    )
    if not mailbox:
        raise HTTPException(status_code=404, detail="Mailbox not found")
    if "quota_mb" in payload:
        mailbox.quota_mb = int(payload["quota_mb"])
    if "is_active" in payload:
        mailbox.is_active = bool(payload["is_active"])
    if "password" in payload and payload["password"]:
        mb_user = await db.get(User, mailbox.user_id)
        if mb_user:
            mb_user.password_hash = hash_password(payload["password"])
    await db.commit()
    return {"ok": True}


@router.delete("/mailboxes/{mailbox_id}")
async def delete_mailbox(
    mailbox_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_domain_admin),
):
    mailbox = await db.scalar(
        select(Mailbox).where(Mailbox.id == mailbox_id, Mailbox.domain_id == user.domain_id)
    )
    if not mailbox:
        raise HTTPException(status_code=404, detail="Mailbox not found")
    await db.delete(mailbox)
    await db.commit()
    return {"ok": True}


# ─── Users ────────────────────────────────────────────────────────────────────

@router.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_domain_admin),
):
    rows = list(
        await db.scalars(
            select(User).where(User.domain_id == user.domain_id).order_by(User.email)
        )
    )
    return [
        {
            "id": row.id,
            "email": row.email,
            "role": row.role.value,
            "is_active": row.is_active,
            "totp_enabled": row.totp_enabled,
        }
        for row in rows
    ]


@router.post("/users")
async def create_user(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_domain_admin),
):
    email: str = payload.get("email", "").strip().lower()
    password: str = payload.get("password", "")
    role_str: str = payload.get("role", "user")

    if not email or not password:
        raise HTTPException(status_code=422, detail="email and password are required")

    existing = await db.scalar(select(User).where(User.email == email))
    if existing:
        raise HTTPException(status_code=409, detail="User already exists")

    role = UserRole(role_str) if role_str in [r.value for r in UserRole] else UserRole.user
    new_user = User(
        email=email,
        password_hash=hash_password(password),
        role=role,
        domain_id=user.domain_id,
        is_active=True,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"id": new_user.id, "email": new_user.email, "role": new_user.role.value}


# ─── Invites ──────────────────────────────────────────────────────────────────

@router.post("/invites")
async def invite_admin(
    payload: InviteCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_domain_admin),
):
    invite = await DomainService(db).invite_domain_admin(user.domain_id, payload.email)

    # Fetch domain name for the email
    domain = await db.scalar(select(Domain).where(Domain.id == user.domain_id))
    domain_name = domain.name if domain else str(user.domain_id)

    email_sent = await send_domain_admin_invite(
        to_email=payload.email,
        domain_name=domain_name,
        invite_token=invite.token,
        invited_by_email=user.email,
    )

    from config import get_settings as _gs  # noqa: PLC0415
    invite_url = f"{_gs().invite_base_url}/invite/{invite.token}"

    return {"token": invite.token, "email_sent": email_sent, "invite_url": invite_url}


# ─── API Keys ─────────────────────────────────────────────────────────────────

@router.get("/api-keys")
async def list_api_keys(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_domain_admin),
):
    try:
        from models.api_key import ApiKey  # noqa: PLC0415
        rows = list(
            await db.scalars(
                select(ApiKey).where(ApiKey.domain_id == user.domain_id)
            )
        )
        return [
            {
                "id": row.id,
                "name": getattr(row, "name", "API Key"),
                "created_at": str(row.created_at) if hasattr(row, "created_at") else None,
                "last_used_at": str(getattr(row, "last_used_at", None)) if getattr(row, "last_used_at", None) else None,
            }
            for row in rows
        ]
    except Exception:
        return []


@router.post("/api-keys")
async def create_api_key(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_domain_admin),
):
    import secrets  # noqa: PLC0415
    try:
        from models.api_key import ApiKey  # noqa: PLC0415
        raw_key = secrets.token_urlsafe(32)
        api_key = ApiKey(
            domain_id=user.domain_id,
            name=payload.get("name", "API Key"),
            key_hash=hash_password(raw_key),
            scopes=payload.get("scopes", []),
        )
        db.add(api_key)
        await db.commit()
        await db.refresh(api_key)
        return {"id": api_key.id, "name": api_key.name, "key": raw_key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# ─── Audit Logs ───────────────────────────────────────────────────────────────

@router.get("/audit-logs")
async def domain_audit_logs(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_domain_admin),
):
    rows = list(
        await db.scalars(
            select(AuditLog)
            .where(AuditLog.user_id == user.id)
            .order_by(AuditLog.created_at.desc())
            .limit(100)
        )
    )
    return [
        {
            "id": row.id,
            "action": row.action,
            "target": row.target,
            "ip_address": row.ip_address,
            "created_at": str(row.created_at),
        }
        for row in rows
    ]


# ─── Settings ─────────────────────────────────────────────────────────────────

@router.get("/settings")
async def get_domain_settings(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_domain_admin),
):
    domain = await db.scalar(select(Domain).where(Domain.id == user.domain_id))
    return {
        "domain_id": user.domain_id,
        "domain_name": domain.name if domain else None,
        "retention_days": getattr(domain, "retention_days", 0) if domain else 0,
        "ediscovery_enabled": getattr(domain, "ediscovery_enabled", False) if domain else False,
    }


@router.put("/settings")
@router.patch("/settings")
async def update_domain_settings(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_domain_admin),
):
    domain = await db.scalar(select(Domain).where(Domain.id == user.domain_id))
    if not domain:
        return {"ok": False}
    for field in ["retention_days", "ediscovery_enabled"]:
        if field in payload and hasattr(domain, field):
            setattr(domain, field, payload[field])
    await db.commit()
    return {"ok": True}


# ─── Whitelabel ───────────────────────────────────────────────────────────────

@router.get("/whitelabel")
async def get_whitelabel(
    domain: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Public endpoint — no auth required — used by login page."""
    if domain:
        domain_row = await db.scalar(select(Domain).where(Domain.name == domain))
    else:
        domain_row = None
    if not domain_row:
        return {"company_name": None, "primary_color": None, "logo_url": None}
    return {
        "company_name": getattr(domain_row, "whitelabel_company_name", None),
        "primary_color": getattr(domain_row, "whitelabel_primary_color", None),
        "logo_url": getattr(domain_row, "whitelabel_logo_url", None),
    }


@router.put("/whitelabel")
@router.patch("/whitelabel")
async def patch_whitelabel(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_domain_admin),
):
    domain = await db.scalar(select(Domain).where(Domain.id == user.domain_id))
    if not domain:
        return {"ok": False}
    field_map = {
        "company_name": "whitelabel_company_name",
        "primary_color": "whitelabel_primary_color",
        "logo_url": "whitelabel_logo_url",
        # also accept raw column names
        "whitelabel_company_name": "whitelabel_company_name",
        "whitelabel_primary_color": "whitelabel_primary_color",
        "whitelabel_logo_url": "whitelabel_logo_url",
    }
    for key, col in field_map.items():
        if key in payload and hasattr(domain, col):
            setattr(domain, col, payload[key])
    await db.commit()
    return {"ok": True}


# ─── Retention ────────────────────────────────────────────────────────────────

@router.put("/retention")
@router.patch("/retention")
async def patch_retention(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_domain_admin),
):
    domain = await db.scalar(select(Domain).where(Domain.id == user.domain_id))
    if not domain or not hasattr(domain, "retention_days"):
        return {"ok": False}
    domain.retention_days = int(payload.get("retention_days", 0))  # type: ignore[attr-defined]
    await db.commit()
    return {"ok": True}


# ─── Shared Mailboxes ─────────────────────────────────────────────────────────

@router.get("/shared-mailboxes")
async def list_shared_mailboxes(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_domain_admin),
):
    rows = list(
        await db.scalars(select(SharedMailbox).where(SharedMailbox.domain_id == user.domain_id))
    )
    return [
        {
            "id": row.id,
            "display_name": getattr(row, "display_name", getattr(row, "address", "Shared mailbox")),
            "address": getattr(row, "address", ""),
        }
        for row in rows
    ]


# ─── eDiscovery ───────────────────────────────────────────────────────────────

@router.post("/ediscovery")
@router.post("/ediscovery/export")
async def create_ediscovery_export(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_domain_admin),
):
    export = EDiscoveryExport(
        domain_id=user.domain_id,
        status="pending",
        query=str(payload),
        export_path=f"/var/backups/email-platform/ediscovery-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}.zip",
        created_at=datetime.now(UTC),
    )
    db.add(export)
    await db.commit()
    await db.refresh(export)
    return {"id": export.id, "status": export.status}


@router.get("/ediscovery")
@router.get("/ediscovery/exports")
async def list_ediscovery_exports(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_domain_admin),
):
    rows = list(
        await db.scalars(
            select(EDiscoveryExport)
            .where(EDiscoveryExport.domain_id == user.domain_id)
            .order_by(EDiscoveryExport.created_at.desc())
        )
    )
    return [
        {
            "id": row.id,
            "status": row.status,
            "query": row.query,
            "created_at": str(row.created_at),
        }
        for row in rows
    ]


# ─── Backup ───────────────────────────────────────────────────────────────────

@router.post("/backup")
async def create_backup(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_domain_admin),
):
    path = await create_domain_backup(user.domain_id, db)
    return {"status": "queued", "file_path": path}
