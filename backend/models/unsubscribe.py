from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


class Unsubscribe(BaseModel):
    __tablename__ = "unsubscribes"

    sender_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    is_unsubscribed: Mapped[bool] = mapped_column(default=True, nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
