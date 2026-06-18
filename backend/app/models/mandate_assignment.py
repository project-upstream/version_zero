from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.mandate import Mandate
    from app.models.user import User


class MandateAssignment(Base):
    __tablename__ = "mandate_assignments"
    __table_args__ = (UniqueConstraint("mandate_id", "user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    mandate_id: Mapped[int] = mapped_column(ForeignKey("mandates.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    mandate: Mapped[Mandate] = relationship("Mandate", back_populates="assignments")
    user: Mapped[User] = relationship("User", back_populates="mandate_assignments")
