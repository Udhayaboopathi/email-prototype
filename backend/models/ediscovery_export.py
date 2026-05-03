from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


class EDiscoveryExport(BaseModel):
    __tablename__ = "ediscovery_exports"

    domain_id: Mapped[str] = mapped_column(ForeignKey("domains.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="queued", nullable=False)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    export_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
