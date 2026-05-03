from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db, require_role
from models.ediscovery_export import EDiscoveryExport
from models.user import UserRole

router = APIRouter(prefix="/ediscovery", tags=["ediscovery"])


@router.post("/export", response_model=dict[str, str])
async def start_export(payload: dict[str, str], db: AsyncSession = Depends(get_db), user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin))):
    row = EDiscoveryExport(domain_id=user.domain_id, status="queued", query=payload.get("query", "ALL"), export_path=f"/var/backups/mail/{user.domain_id}-ediscovery.tar.gz")
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return {"id": row.id, "status": row.status}


@router.get("/", response_model=list[dict[str, str]])
async def list_exports(db: AsyncSession = Depends(get_db), user=Depends(require_role(UserRole.domain_admin, UserRole.super_admin))):
    rows = await db.scalars(select(EDiscoveryExport).where(EDiscoveryExport.domain_id == user.domain_id))
    return [{"id": row.id, "status": row.status, "path": row.export_path} for row in rows]
