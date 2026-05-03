from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


class LoginActivity(BaseModel):
    __tablename__ = "login_activities"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(64), nullable=False)
    country: Mapped[str] = mapped_column(String(64), nullable=False, default="Unknown")
    user_agent: Mapped[str] = mapped_column(String(512), nullable=False, default="unknown")
    success: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
