from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db, require_role
from core.security import hash_password
from models.audit_log import AuditLog
from models.domain import Domain
from models.ediscovery_export import EDiscoveryExport
from models.mailbox import Mailbox
from models.shared_mailbox import SharedMailbox
from models.user import User, UserRole
from schemas.domain import DomainResponse, InviteCreate
from services.backup_service import create_domain_backup
from services.domain_service import DomainService

router = APIRouter(prefix="/domain-admin", tags=["domain-admin"])


# ─── Domain info ──────────────────────────────────────────────────────────────

@router.get("/domain", response_model=DomainResponse)
async def my_domain(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin)),
):
    domain = await db.scalar(select(Domain).where(Domain.id == user.domain_id))
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    return DomainResponse(
        id=domain.id, name=domain.name, is_verified=domain.is_verified, created_at=domain.created_at
    )


@router.get("/me")
async def me(user=Depends(get_current_user)):
    return {"email": user.email, "role": user.role.value, "domain_id": user.domain_id}


# ─── Stats ────────────────────────────────────────────────────────────────────

@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin)),
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
    user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin)),
):
    domain = await db.scalar(select(Domain).where(Domain.id == user.domain_id))
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    domain_name = domain.name
    return [
        {"type": "MX", "name": domain_name, "value": f"mail.{domain_name}", "ttl": "3600", "priority": "10", "purpose": "Receive email"},
        {"type": "A", "name": f"mail.{domain_name}", "value": "YOUR_SERVER_IP", "ttl": "3600", "priority": "", "purpose": "Mail server IP"},
        {"type": "TXT", "name": domain_name, "value": f"v=spf1 mx a:{domain_name} ~all", "ttl": "3600", "priority": "", "purpose": "SPF — prevent spoofing"},
        {"type": "TXT", "name": f"_dmarc.{domain_name}", "value": f"v=DMARC1; p=quarantine; rua=mailto:admin@{domain_name}", "ttl": "3600", "priority": "", "purpose": "DMARC policy"},
        {"type": "TXT", "name": f"mail._domainkey.{domain_name}", "value": domain.dkim_public_key or "DKIM key not yet generated — restart the backend to generate", "ttl": "3600", "priority": "", "purpose": "DKIM email signing"},
    ]


# ─── Mailboxes ────────────────────────────────────────────────────────────────

@router.get("/mailboxes")
async def list_mailboxes(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin)),
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
    payload: dict,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin)),
):
    domain = await db.scalar(select(Domain).where(Domain.id == user.domain_id))
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    local_part: str = payload.get("local_part", "").strip().lower()
    password: str = payload.get("password", "")
    quota_mb: int = int(payload.get("quota_mb", 2048))

    if not local_part or not password:
        raise HTTPException(status_code=422, detail="local_part and password are required")

    email_address = f"{local_part}@{domain.name}"

    # Check if mailbox already exists
    existing = await db.scalar(select(Mailbox).where(Mailbox.address == email_address))
    if existing:
        raise HTTPException(status_code=409, detail="Mailbox already exists")

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

    mailbox = Mailbox(
        domain_id=user.domain_id,
        user_id=mailbox_user.id,
        address=email_address,
        quota_mb=quota_mb,
        is_active=True,
    )
    db.add(mailbox)
    await db.commit()
    await db.refresh(mailbox)

    return {
        "id": mailbox.id,
        "email": mailbox.address,
        "quota_mb": mailbox.quota_mb,
        "is_active": mailbox.is_active,
    }


@router.patch("/mailboxes/{mailbox_id}")
async def update_mailbox(
    mailbox_id: str,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin)),
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
    user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin)),
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
    user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin)),
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
    user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin)),
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
    user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin)),
):
    invite = await DomainService(db).invite_domain_admin(user.domain_id, payload.email)
    return {"token": invite.token}


# ─── API Keys ─────────────────────────────────────────────────────────────────

@router.get("/api-keys")
async def list_api_keys(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin)),
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
    user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin)),
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
    user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin)),
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
    user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin)),
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
    user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin)),
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
    user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin)),
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
    user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin)),
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
    user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin)),
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
    user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin)),
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
    user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin)),
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
    user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin)),
):
    path = await create_domain_backup(user.domain_id, db)
    return {"status": "queued", "file_path": path}
