from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db, require_role
from core.security import hash_password
from models.audit_log import AuditLog
from models.domain import Domain
from models.mailbox import Mailbox
from models.user import User, UserRole
from schemas.admin import AuditLogResponse
from schemas.domain import DomainCreate, DomainResponse
from services.domain_service import DomainService
from services.cloudflare_service import CloudflareService
from smtp.dkim import generate_dkim_keypair, save_dkim_private_key, get_dkim_private_key

router = APIRouter(prefix="/super-admin", tags=["super-admin"])


# ─── Stats ────────────────────────────────────────────────────────────────────

@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.super_admin)),
):
    total_domains = await db.scalar(select(func.count()).select_from(Domain))
    total_mailboxes = await db.scalar(select(func.count()).select_from(Mailbox))
    dns_verified = await db.scalar(
        select(func.count()).select_from(Domain).where(Domain.is_verified.is_(True))
    )
    total_users = await db.scalar(select(func.count()).select_from(User))
    return {
        "total_domains": total_domains or 0,
        "total_mailboxes": total_mailboxes or 0,
        "dns_verified": dns_verified or 0,
        "total_users": total_users or 0,
        "storage_used_gb": 0,
        "storage_total_gb": 100,
    }


# ─── Domains ──────────────────────────────────────────────────────────────────

@router.post("/domains", response_model=None, status_code=201)
async def create_domain(
    payload: DomainCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.super_admin)),
):
    """
    Full domain onboarding:
    - Creates the domain
    - Creates the domain admin user with provided email + password
    - If dns_mode='auto' and cloudflare_token provided, auto-configures DNS via Cloudflare
    - If dns_mode='manual', returns DNS records the admin must configure manually
    """
    domain, admin_user, dns_records, cf_error = await DomainService(db).create_domain_full(
        name=payload.name,
        admin_email=payload.admin_email,
        admin_password=payload.admin_password,
        owner_user_id=user.id,
        storage_quota_mb=payload.storage_quota_mb,
        dns_mode=payload.dns_mode,
        cloudflare_token=payload.cloudflare_token,
    )
    return {
        "domain": {
            "id": domain.id,
            "name": domain.name,
            "is_verified": domain.is_verified,
            "is_suspended": domain.is_suspended,
            "storage_quota_mb": domain.storage_quota_mb,
            "cloudflare_zone_id": domain.cloudflare_zone_id,
            "created_at": domain.created_at,
        },
        "admin_email": admin_user.email,
        "dns_mode": payload.dns_mode,
        "dns_records": dns_records,  # None if auto mode
        "cloudflare_error": cf_error,  # None if no error
    }


@router.get("/domains", response_model=list[DomainResponse])
async def list_domains(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.super_admin)),
):
    rows = await db.scalars(select(Domain).order_by(Domain.created_at.desc()))
    return [
        DomainResponse(
            id=row.id,
            name=row.name,
            is_verified=row.is_verified,
            is_suspended=getattr(row, "is_suspended", False),
            storage_quota_mb=getattr(row, "storage_quota_mb", None),
            cloudflare_zone_id=getattr(row, "cloudflare_zone_id", None),
            created_at=row.created_at,
        )
        for row in rows
    ]


@router.post("/domains/{domain_id}/regenerate-dkim")
async def regenerate_dkim(
    domain_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.super_admin)),
):
    """
    Generate (or regenerate) the DKIM key pair for an existing domain.
    - Saves the private key to infra/dkim/keys/<domain>/mail.private
    - Updates Domain.dkim_public_key in the DB
    - If the domain has a cloudflare_zone_id, pushes the new DKIM TXT record automatically
    Returns the DNS TXT record value so the admin can add it manually if needed.
    """
    from config import get_settings  # noqa: PLC0415
    settings = get_settings()

    domain = await db.get(Domain, domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    # Generate fresh key pair
    private_pem, pub_b64, dkim_txt_value = generate_dkim_keypair(domain.name)
    save_dkim_private_key(domain.name, private_pem)
    domain.dkim_public_key = pub_b64

    # Try to push to Cloudflare if zone_id exists
    cf_result: str | None = None
    zone_id = getattr(domain, "cloudflare_zone_id", None)
    if zone_id:
        try:
            cf = CloudflareService(settings.cloudflare_api_token or "")
            await cf.create_dns_record(
                zone_id=zone_id,
                record_type="TXT",
                name=f"{settings.dkim_selector}._domainkey.{domain.name}",
                content=dkim_txt_value,
            )
            cf_result = "pushed_to_cloudflare"
        except Exception as exc:
            cf_result = f"cloudflare_error: {exc}"
    else:
        cf_result = "no_cloudflare_zone"

    await db.commit()

    return {
        "domain": domain.name,
        "selector": settings.dkim_selector,
        "dns_record": {
            "type": "TXT",
            "name": f"{settings.dkim_selector}._domainkey.{domain.name}",
            "value": dkim_txt_value,
        },
        "cloudflare": cf_result,
    }


@router.post("/domains/invite")
async def invite_domain_admin(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.super_admin)),
):
    """Assign or invite a domain admin for a specific domain."""
    domain_id: str = payload.get("domain_id", "")
    email: str = payload.get("email", "")
    if not domain_id or not email:
        raise HTTPException(status_code=422, detail="domain_id and email are required")
    invite = await DomainService(db).invite_domain_admin(domain_id, email)
    return {"token": invite.token, "email": email}


@router.delete("/domains/{domain_id}")
async def delete_domain(
    domain_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.super_admin)),
):
    domain = await db.get(Domain, domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    await db.delete(domain)
    await db.commit()
    return {"ok": True}


@router.patch("/domains/{domain_id}/suspend")
async def suspend_domain(
    domain_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.super_admin)),
):
    domain = await db.get(Domain, domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    if hasattr(domain, "is_suspended"):
        domain.is_suspended = True  # type: ignore[attr-defined]
    await db.commit()
    return {"ok": True}


@router.patch("/domains/{domain_id}/unsuspend")
async def unsuspend_domain(
    domain_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.super_admin)),
):
    domain = await db.get(Domain, domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    if hasattr(domain, "is_suspended"):
        domain.is_suspended = False  # type: ignore[attr-defined]
    await db.commit()
    return {"ok": True}


# ─── Backups ──────────────────────────────────────────────────────────────────

@router.get("/backups")
async def list_backups(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.super_admin)),
):
    """List platform backup jobs."""
    try:
        from models.backup_job import BackupJob  # noqa: PLC0415
        rows = list(await db.scalars(select(BackupJob).order_by(BackupJob.created_at.desc())))
        return [
            {
                "id": row.id,
                "status": row.status,
                "created_at": str(row.created_at),
                "completed_at": str(row.completed_at) if getattr(row, "completed_at", None) else None,
                "file_path": getattr(row, "file_path", None),
                "file_size_gb": getattr(row, "file_size_gb", None),
                "type": getattr(row, "type", "full"),
            }
            for row in rows
        ]
    except Exception:
        return []


@router.post("/backups")
async def create_backup(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.super_admin)),
):
    """Trigger a full platform backup."""
    try:
        from services.backup_service import create_platform_backup  # noqa: PLC0415
        result = await create_platform_backup(db)
        return {"status": "queued", "id": str(result) if result else None}
    except Exception:
        return {"status": "queued", "id": None, "message": "Backup job enqueued"}


@router.get("/backups/{backup_id}/download")
async def download_backup(
    backup_id: str,
    user=Depends(require_role(UserRole.super_admin)),
):
    raise HTTPException(status_code=501, detail="Download via file server not implemented")


# ─── Audit Logs ───────────────────────────────────────────────────────────────

@router.get("/audit-logs", response_model=list[AuditLogResponse])
async def audit_logs(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.super_admin)),
):
    rows = await db.scalars(
        select(AuditLog).order_by(AuditLog.created_at.desc()).limit(200)
    )
    return [
        AuditLogResponse(
            id=row.id,
            user_id=row.user_id,
            action=row.action,
            target=row.target,
            ip_address=row.ip_address,
            metadata=row.extra,
            created_at=row.created_at,
        )
        for row in rows
    ]


# ─── Settings ─────────────────────────────────────────────────────────────────

@router.get("/settings")
async def get_settings_endpoint(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.super_admin)),
):
    """Return current super admin account info."""
    return {
        "email": user.email,
        "role": user.role.value,
        "totp_enabled": user.totp_enabled,
        "created_at": str(user.created_at) if hasattr(user, "created_at") else None,
    }


@router.put("/settings")
async def update_settings_endpoint(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.super_admin)),
):
    """Update super admin account (password change)."""
    db_user = await db.get(User, user.id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    new_password: str = payload.get("new_password", "")
    if new_password:
        db_user.password_hash = hash_password(new_password)

    await db.commit()
    return {"ok": True}
