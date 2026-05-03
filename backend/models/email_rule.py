from sqlalchemy import Boolean, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


class EmailRule(BaseModel):
    __tablename__ = "email_rules"

    mailbox_id: Mapped[str] = mapped_column(ForeignKey("mailboxes.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    conditions: Mapped[dict[str, str]] = mapped_column(JSON, nullable=False, default=dict)
    actions: Mapped[dict[str, str]] = mapped_column(JSON, nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
