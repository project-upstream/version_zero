"""Cadence service — schedule lifecycle + computed fields (plan.md §5.2).

Rules (locked, do not deviate):
- AWAITING_INITIAL: no initial_date; clock does not tick.
- ACTIVE: initial_date set on first INITIAL_EMAIL; fixed-anchor follow-ups.
- STOPPED: terminal (or MANUAL-paused, which can be resumed).
- initial_date is immutable once set.
- All date math uses today_ist() (Asia/Kolkata).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.time import today_ist
from app.models.enums import (
    CompanyStatus,
    OutreachEventType,
    ScheduleStatus,
    StoppedReason,
)
from app.models.outreach_event import OutreachEvent
from app.models.outreach_schedule import OutreachSchedule


async def get_followups_done(db: AsyncSession, schedule_id: int) -> int:
    """Count FOLLOW_UP events for this schedule."""
    result = await db.execute(
        select(func.count()).select_from(OutreachEvent).where(
            OutreachEvent.schedule_id == schedule_id,
            OutreachEvent.event_type == OutreachEventType.FOLLOW_UP,
        )
    )
    return result.scalar() or 0


def compute_cadence(sched: OutreachSchedule, followups_done: int) -> dict:
    """Return cadence computed fields for one schedule (§5.2).

    next_due_date = initial_date + (followups_done+1) * cadence_interval_days
    """
    if sched.status != ScheduleStatus.ACTIVE or sched.initial_date is None:
        return {
            "schedule_status": sched.status,
            "initial_date": sched.initial_date,
            "next_due_date": None,
            "days_remaining": None,
            "is_overdue": False,
        }
    today = today_ist()
    n = followups_done + 1
    next_due: date = sched.initial_date + timedelta(days=n * sched.cadence_interval_days)
    days_remaining = (next_due - today).days
    return {
        "schedule_status": sched.status,
        "initial_date": sched.initial_date,
        "next_due_date": next_due,
        "days_remaining": days_remaining,
        "is_overdue": days_remaining < 0,
    }


async def activate_schedule(
    db: AsyncSession, sched: OutreachSchedule, initial_date: date
) -> None:
    """Transition AWAITING_INITIAL → ACTIVE on the first INITIAL_EMAIL (E-01)."""
    if sched.initial_date is not None:
        return  # immutable — already activated; log the event but don't change the date
    sched.status = ScheduleStatus.ACTIVE
    sched.initial_date = initial_date


async def stop_schedule(
    db: AsyncSession,
    sched: OutreachSchedule,
    reason: StoppedReason,
) -> None:
    """Transition any active schedule → STOPPED."""
    sched.status = ScheduleStatus.STOPPED
    sched.stopped_reason = reason
    sched.stopped_at = datetime.now(timezone.utc)


async def pause_schedule(db: AsyncSession, sched: OutreachSchedule) -> None:
    """Manual pause (STOPPED + reason=MANUAL)."""
    await stop_schedule(db, sched, StoppedReason.MANUAL)


async def resume_schedule(db: AsyncSession, sched: OutreachSchedule) -> None:
    """Resume a manually-paused schedule → ACTIVE."""
    if sched.stopped_reason != StoppedReason.MANUAL:
        return  # only manual pauses are resumable
    if sched.initial_date is None:
        sched.status = ScheduleStatus.AWAITING_INITIAL
    else:
        sched.status = ScheduleStatus.ACTIVE
    sched.stopped_reason = None
    sched.stopped_at = None


# ── Status-to-StoppedReason mapping ──────────────────────────────────────────

_STATUS_TO_REASON: dict[CompanyStatus, StoppedReason] = {
    CompanyStatus.RESPONDED: StoppedReason.RESPONDED,
    CompanyStatus.BOUNCED: StoppedReason.BOUNCED,
    CompanyStatus.DECLINED: StoppedReason.DECLINED,
}

EVENT_STOP_MAP: dict[OutreachEventType, StoppedReason] = {
    OutreachEventType.RESPONSE: StoppedReason.RESPONDED,
    OutreachEventType.BOUNCE: StoppedReason.BOUNCED,
}

EVENT_STATUS_MAP: dict[OutreachEventType, CompanyStatus] = {
    OutreachEventType.RESPONSE: CompanyStatus.RESPONDED,
    OutreachEventType.BOUNCE: CompanyStatus.BOUNCED,
}
