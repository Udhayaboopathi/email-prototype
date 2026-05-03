from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


class Alias(BaseModel):
    __tablename__ = "aliases"

    domain_id: Mapped[str] = mapped_column(ForeignKey("domains.id", ondelete="CASCADE"), nullable=False)
    source: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    destination: Mapped[str] = mapped_column(String(320), nullable=False)
