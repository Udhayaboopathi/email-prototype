from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db, require_role
from models.audit_log import AuditLog
from models.domain import Domain
from models.user import UserRole
from schemas.admin import AuditLogResponse
from schemas.domain import DomainCreate, DomainResponse
from services.domain_service import DomainService

router = APIRouter(prefix="/super-admin", tags=["super-admin"])


@router.post("/domains", response_model=DomainResponse)
async def create_domain(payload: DomainCreate, db: AsyncSession = Depends(get_db), user=Depends(require_role(UserRole.super_admin))):
    domain = await DomainService(db).create_domain(payload.name, user.id)
    return DomainResponse(id=domain.id, name=domain.name, is_verified=domain.is_verified, created_at=domain.created_at)


@router.get("/domains", response_model=list[DomainResponse])
async def list_domains(db: AsyncSession = Depends(get_db), user=Depends(require_role(UserRole.super_admin))):
    rows = await db.scalars(select(Domain).order_by(Domain.created_at.desc()))
    return [DomainResponse(id=row.id, name=row.name, is_verified=row.is_verified, created_at=row.created_at) for row in rows]


@router.get("/audit-logs", response_model=list[AuditLogResponse])
async def audit_logs(db: AsyncSession = Depends(get_db), user=Depends(require_role(UserRole.super_admin))):
    rows = await db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(200))
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
