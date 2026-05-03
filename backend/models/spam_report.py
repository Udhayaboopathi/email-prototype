from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


class SpamReport(BaseModel):
    __tablename__ = "spam_reports"

    email_uid: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    reporter_user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
