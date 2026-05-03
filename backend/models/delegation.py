from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


class Delegation(BaseModel):
    __tablename__ = "delegations"

    shared_mailbox_id: Mapped[str] = mapped_column(ForeignKey("shared_mailboxes.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    can_send: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_read: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_manage: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
