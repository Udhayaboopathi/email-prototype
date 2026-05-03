from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


class Domain(BaseModel):
    __tablename__ = "domains"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    dkim_public_key: Mapped[str | None] = mapped_column(String(4096), nullable=True)
    owner_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
