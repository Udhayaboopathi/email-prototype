from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


class ReadReceipt(BaseModel):
    __tablename__ = "read_receipts"

    email_uid: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
