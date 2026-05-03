from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


class TrackingPixel(BaseModel):
    __tablename__ = "tracking_pixels"

    email_uid: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    pixel_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    opened_count: Mapped[int] = mapped_column(default=0, nullable=False)
    last_opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
