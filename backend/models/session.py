from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


class Session(BaseModel):
    __tablename__ = "sessions"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    refresh_token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    user_agent: Mapped[str] = mapped_column(String(512), nullable=False, default="unknown")
    ip_address: Mapped[str] = mapped_column(String(64), nullable=False, default="0.0.0.0")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
