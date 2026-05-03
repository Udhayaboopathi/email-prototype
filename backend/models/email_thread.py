from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


class EmailThread(BaseModel):
    __tablename__ = "email_threads"

    mailbox_id: Mapped[str] = mapped_column(ForeignKey("mailboxes.id", ondelete="CASCADE"), nullable=False)
    subject: Mapped[str] = mapped_column(String(998), nullable=False)
    snippet: Mapped[str] = mapped_column(Text, nullable=False, default="")
    last_message_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
