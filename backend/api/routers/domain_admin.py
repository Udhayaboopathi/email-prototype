from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db, require_role
from models.ediscovery_export import EDiscoveryExport
from models.domain import Domain
from models.shared_mailbox import SharedMailbox
from models.user import UserRole
from schemas.domain import DomainResponse, InviteCreate
from services.backup_service import create_domain_backup
from services.domain_service import DomainService

router = APIRouter(prefix="/domain-admin", tags=["domain-admin"])


@router.get("/domain", response_model=DomainResponse)
async def my_domain(db: AsyncSession = Depends(get_db), user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin))):
    domain = await db.scalar(select(Domain).where(Domain.id == user.domain_id))
    return DomainResponse(id=domain.id, name=domain.name, is_verified=domain.is_verified, created_at=domain.created_at)


@router.get("/dns-guide", response_model=list[dict[str, str]])
async def dns_guide(user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin))):
    domain = user.email.split("@", 1)[1]
    return await DomainService.__new__(DomainService).dns_guide.records_for_domain(domain)  # type: ignore[attr-defined]


@router.post("/invites", response_model=dict[str, str])
async def invite_admin(payload: InviteCreate, db: AsyncSession = Depends(get_db), user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin))):
    invite = await DomainService(db).invite_domain_admin(user.domain_id, payload.email)
    return {"token": invite.token}


@router.get("/me", response_model=dict[str, str])
async def me(user=Depends(get_current_user)):
    return {"email": user.email, "role": user.role.value}


@router.post("/backup", response_model=dict[str, str])
async def create_backup(db: AsyncSession = Depends(get_db), user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin))):
    path = await create_domain_backup(user.domain_id, db)
    return {"status": "queued", "file_path": path}


@router.get("/shared-mailboxes", response_model=list[dict[str, str]])
async def list_shared_mailboxes(db: AsyncSession = Depends(get_db), user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin))):
    rows = list(await db.scalars(select(SharedMailbox).where(SharedMailbox.domain_id == user.domain_id)))
    return [{"id": row.id, "display_name": getattr(row, "display_name", getattr(row, "address", "Shared mailbox"))} for row in rows]


@router.get("/whitelabel", response_model=dict[str, str | None])
async def get_whitelabel(
    domain: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
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


@router.patch("/whitelabel", response_model=dict[str, bool])
async def patch_whitelabel(payload: dict[str, str], db: AsyncSession = Depends(get_db), user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin))):
    domain = await db.scalar(select(Domain).where(Domain.id == user.domain_id))
    if not domain:
        return {"ok": False}
    for key in ["whitelabel_company_name", "whitelabel_primary_color", "whitelabel_logo_url"]:
        if key in payload and hasattr(domain, key):
            setattr(domain, key, payload[key])
    await db.commit()
    return {"ok": True}


@router.patch("/retention", response_model=dict[str, bool])
async def patch_retention(payload: dict[str, int], db: AsyncSession = Depends(get_db), user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin))):
    domain = await db.scalar(select(Domain).where(Domain.id == user.domain_id))
    if not domain or not hasattr(domain, "retention_days"):
        return {"ok": False}
    domain.retention_days = int(payload.get("retention_days", 0))
    await db.commit()
    return {"ok": True}


@router.post("/ediscovery/export", response_model=dict[str, str])
async def create_ediscovery_export(payload: dict[str, str], db: AsyncSession = Depends(get_db), user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin))):
    export = EDiscoveryExport(
        domain_id=user.domain_id,
        status="pending",
        query=payload.get("query", ""),
        export_path=f"/var/backups/email-platform/ediscovery-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}.zip",
        created_at=datetime.now(UTC),
    )
    db.add(export)
    await db.commit()
    await db.refresh(export)
    return {"id": export.id, "status": export.status}
