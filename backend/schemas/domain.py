from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class DomainCreate(BaseModel):
    # Core domain identity
    name: str = Field(..., description="Domain name, e.g. example.com")

    # Domain admin account (created immediately on domain creation)
    admin_email: EmailStr = Field(..., description="Email for the domain admin account (must match the domain)")
    admin_password: str = Field(..., min_length=8, description="Initial password for the domain admin")

    # Storage quota
    storage_quota_mb: int | None = Field(
        None, ge=100, description="Storage quota in MB (None = unlimited)"
    )

    # DNS configuration mode
    dns_mode: Literal["auto", "manual"] = Field(
        "manual", description="'auto' = configure via Cloudflare API, 'manual' = show guide"
    )
    cloudflare_token: str | None = Field(
        None, description="Cloudflare API token (required when dns_mode='auto')"
    )


class DomainResponse(BaseModel):
    id: str
    name: str
    is_verified: bool
    is_suspended: bool
    storage_quota_mb: int | None
    cloudflare_zone_id: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class InviteCreate(BaseModel):
    email: str
