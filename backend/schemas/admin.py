from datetime import datetime

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: str
    user_id: str | None
    action: str
    target: str
    ip_address: str
    metadata: dict[str, str]
    created_at: datetime


class StorageStatsResponse(BaseModel):
    used_mb: int
    quota_mb: int
    usage_percent: float
