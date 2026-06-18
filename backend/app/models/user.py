from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum as SAEnum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import UserRole

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.contact import Contact
    from app.models.firm import Firm
    from app.models.mandate import Mandate
    from app.models.mandate_assignment import MandateAssignment
    from app.models.outreach_event import OutreachEvent
    from app.models.refresh_token import RefreshToken


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    firm_id: Mapped[int] = mapped_column(ForeignKey("firms.id"), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole, native_enum=False), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    token_version: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    firm: Mapped[Firm] = relationship("Firm", back_populates="users")
    refresh_tokens: Mapped[list[RefreshToken]] = relationship(
        "RefreshToken", back_populates="user"
    )
    mandate_assignments: Mapped[list[MandateAssignment]] = relationship(
        "MandateAssignment", back_populates="user"
    )
    led_mandates: Mapped[list[Mandate]] = relationship("Mandate", back_populates="lead_owner")
    created_companies: Mapped[list[Company]] = relationship(
        "Company", back_populates="created_by"
    )
    poc_contacts: Mapped[list[Contact]] = relationship("Contact", back_populates="poc_owner")
    owned_events: Mapped[list[OutreachEvent]] = relationship(
        "OutreachEvent", back_populates="owner"
    )
