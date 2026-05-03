from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


class Label(BaseModel):
    __tablename__ = "labels"

    mailbox_id: Mapped[str] = mapped_column(ForeignKey("mailboxes.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str] = mapped_column(String(16), default="#3b82f6", nullable=False)
