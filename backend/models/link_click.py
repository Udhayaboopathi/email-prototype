from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


class LinkClick(BaseModel):
    __tablename__ = "link_clicks"

    email_uid: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    ip_address: Mapped[str] = mapped_column(String(64), nullable=False)
    user_agent: Mapped[str] = mapped_column(String(512), nullable=False)
