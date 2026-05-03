from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


class Domain(BaseModel):
    __tablename__ = "domains"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_suspended: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    dkim_public_key: Mapped[str | None] = mapped_column(String(4096), nullable=True)
    owner_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    # Storage quota in MB (None = unlimited)
    storage_quota_mb: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    # Cloudflare zone ID stored after auto-DNS configuration
    cloudflare_zone_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
