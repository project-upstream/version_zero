from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Enum as SAEnum, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ScheduleStatus, StoppedReason

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.firm import Firm
    from app.models.outreach_event import OutreachEvent


class OutreachSchedule(Base):
    __tablename__ = "outreach_schedules"

    id: Mapped[int] = mapped_column(primary_key=True)
    firm_id: Mapped[int] = mapped_column(ForeignKey("firms.id"), nullable=False, index=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"), nullable=False, unique=True
    )
    status: Mapped[ScheduleStatus] = mapped_column(
        SAEnum(ScheduleStatus, native_enum=False),
        nullable=False,
        default=ScheduleStatus.AWAITING_INITIAL,
    )
    initial_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    cadence_interval_days: Mapped[int] = mapped_column(Integer, default=14, nullable=False)
    regarding: Mapped[str | None] = mapped_column(Text, nullable=True)
    stopped_reason: Mapped[StoppedReason | None] = mapped_column(
        SAEnum(StoppedReason, native_enum=False), nullable=True
    )
    stopped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    firm: Mapped[Firm] = relationship("Firm")
    company: Mapped[Company] = relationship("Company", back_populates="outreach_schedule")
    outreach_events: Mapped[list[OutreachEvent]] = relationship(
        "OutreachEvent", back_populates="schedule"
    )
