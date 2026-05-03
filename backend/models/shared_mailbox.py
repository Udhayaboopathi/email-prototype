from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


class SharedMailbox(BaseModel):
    __tablename__ = "shared_mailboxes"

    domain_id: Mapped[str] = mapped_column(ForeignKey("domains.id", ondelete="CASCADE"), nullable=False)
    address: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
