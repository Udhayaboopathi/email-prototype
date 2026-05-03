from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


class Mailbox(BaseModel):
    __tablename__ = "mailboxes"

    domain_id: Mapped[str] = mapped_column(ForeignKey("domains.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    address: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    quota_mb: Mapped[int] = mapped_column(default=2048, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
