from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


class BackupJob(BaseModel):
    __tablename__ = "backup_jobs"

    type: Mapped[str] = mapped_column(String(20), default="scheduled", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="running", nullable=False)
    domain_id: Mapped[str | None] = mapped_column(ForeignKey("domains.id", ondelete="SET NULL"), nullable=True)
    mailbox_id: Mapped[str | None] = mapped_column(ForeignKey("mailboxes.id", ondelete="SET NULL"), nullable=True)
    file_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_size_mb: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_messages: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
