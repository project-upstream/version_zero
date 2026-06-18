"""Analytics queries — overview, response-by-bucket, by-analyst, sources (A-01/A-02)."""

from __future__ import annotations

from datetime import timedelta

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.time import today_ist
from app.models.company import Company
from app.models.enums import (
    CompanyStatus,
    OutreachEventType,
    ScheduleStatus,
    Source,
    SourceQuality,
)
from app.models.outreach_event import OutreachEvent
from app.models.outreach_schedule import OutreachSchedule
from app.models.user import User

# "Responded" is defined once and reused everywhere (§5.4):
# company.status == RESPONDED OR a RESPONSE event exists for the company.
# For aggregate queries we use status == RESPONDED (single source of truth since
# POST /events sets the status on RESPONSE — they stay in sync).
RESPONDED_STATUS = CompanyStatus.RESPONDED


async def get_overview(
    db: AsyncSession,
    firm_id: int,
    mandate_ids: list[int] | None,
) -> dict:
    """Counts by status/type, % responded, due-this-week, overdue, needs-initial."""
    base = select(Company).where(
        Company.firm_id == firm_id,
        Company.archived_at.is_(None),
    )
    if mandate_ids is not None:
        base = base.where(Company.mandate_id.in_(mandate_ids))

    result = await db.execute(base)
    companies = result.scalars().all()

    total = len(companies)
    by_status: dict[str, int] = {}
    for c in companies:
        key = c.status.value
        by_status[key] = by_status.get(key, 0) + 1

    responded = by_status.get(RESPONDED_STATUS.value, 0)
    responded_pct = round(responded / total, 4) if total else 0.0

    # Schedule-based counts: query schedules for these companies
    company_ids = [c.id for c in companies]
    if not company_ids:
        return {
            "total": 0,
            "by_status": by_status,
            "responded_pct": 0.0,
            "due_this_week": 0,
            "overdue": 0,
            "needs_initial": 0,
            "active_mandates": 0,
        }

    sched_result = await db.execute(
        select(OutreachSchedule).where(OutreachSchedule.company_id.in_(company_ids))
    )
    schedules = sched_result.scalars().all()

    today = today_ist()
    window_end = today + timedelta(days=7)

    needs_initial = sum(1 for s in schedules if s.status == ScheduleStatus.AWAITING_INITIAL)
    overdue = 0
    due_this_week = 0
    for s in schedules:
        if s.status != ScheduleStatus.ACTIVE or s.initial_date is None:
            continue
        # Count follow-ups done: requires event query per schedule — use schedule.id
        # We approximate by computing from events later; for now just use schedule data
        # Since followups_done requires event count, we skip the exact math and delegate
        # to the cadence service. Instead compute from a simpler approach:
        # next_due = initial_date + (fu+1) * interval — we precompute below.
        pass

    # Batch: count follow-ups per schedule_id from events table
    fu_result = await db.execute(
        select(
            OutreachEvent.schedule_id,
            func.count(OutreachEvent.id).label("cnt"),
        )
        .where(
            OutreachEvent.schedule_id.in_([s.id for s in schedules if s.id]),
            OutreachEvent.event_type == OutreachEventType.FOLLOW_UP,
        )
        .group_by(OutreachEvent.schedule_id)
    )
    fu_by_sched = {row.schedule_id: row.cnt for row in fu_result.all()}

    for s in schedules:
        if s.status != ScheduleStatus.ACTIVE or s.initial_date is None:
            continue
        fu_done = fu_by_sched.get(s.id, 0)
        next_due = s.initial_date + timedelta(days=(fu_done + 1) * s.cadence_interval_days)
        days_remaining = (next_due - today).days
        if days_remaining < 0:
            overdue += 1
        if days_remaining <= 7:
            due_this_week += 1

    # Active mandates (distinct mandate_ids in scope)
    active_mandate_ids = len({c.mandate_id for c in companies})

    return {
        "total": total,
        "by_status": by_status,
        "responded_pct": responded_pct,
        "due_this_week": due_this_week,
        "overdue": overdue,
        "needs_initial": needs_initial,
        "active_mandates": active_mandate_ids,
    }


async def get_response_by_bucket(
    db: AsyncSession,
    firm_id: int,
    mandate_ids: list[int] | None,
) -> list[dict]:
    """Response rate grouped by bucket (A-01)."""
    stmt = (
        select(
            Company.bucket,
            func.count(Company.id).label("total"),
            func.sum(
                case((Company.status == RESPONDED_STATUS, 1), else_=0)
            ).label("responded"),
        )
        .where(
            Company.firm_id == firm_id,
            Company.archived_at.is_(None),
        )
        .group_by(Company.bucket)
        .order_by(func.count(Company.id).desc())
    )
    if mandate_ids is not None:
        stmt = stmt.where(Company.mandate_id.in_(mandate_ids))

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "bucket": row.bucket or "Unassigned",
            "total": row.total,
            "responded": int(row.responded or 0),
            "response_rate": round(int(row.responded or 0) / row.total, 4) if row.total else 0.0,
        }
        for row in rows
    ]


async def get_by_analyst(
    db: AsyncSession,
    firm_id: int,
) -> list[dict]:
    """Volume / responses / conversion per analyst (A-02). Partner-only endpoint."""
    # Count outreach events per owner within the firm
    events_stmt = (
        select(
            OutreachEvent.owner_id,
            func.count(OutreachEvent.id).label("total_events"),
            func.sum(
                case((OutreachEvent.event_type == OutreachEventType.INITIAL_EMAIL, 1), else_=0)
            ).label("initial_emails"),
            func.sum(
                case((OutreachEvent.event_type == OutreachEventType.RESPONSE, 1), else_=0)
            ).label("responses"),
        )
        .where(OutreachEvent.firm_id == firm_id)
        .group_by(OutreachEvent.owner_id)
    )
    events_result = await db.execute(events_stmt)
    events_by_owner = {
        row.owner_id: {
            "total_events": row.total_events,
            "initial_emails": int(row.initial_emails or 0),
            "responses": int(row.responses or 0),
        }
        for row in events_result.all()
    }

    # Fetch user names
    user_result = await db.execute(
        select(User).where(User.firm_id == firm_id, User.is_active.is_(True))
    )
    users = user_result.scalars().all()

    out = []
    for u in users:
        stats = events_by_owner.get(u.id, {"total_events": 0, "initial_emails": 0, "responses": 0})
        total = stats["initial_emails"]
        responses = stats["responses"]
        out.append(
            {
                "user_id": u.id,
                "full_name": u.full_name,
                "role": u.role.value,
                "total_events": stats["total_events"],
                "initial_emails": total,
                "responses": responses,
                "conversion_rate": round(responses / total, 4) if total else 0.0,
            }
        )
    return sorted(out, key=lambda x: x["total_events"], reverse=True)


async def get_sources(
    db: AsyncSession,
    firm_id: int,
    mandate_ids: list[int] | None,
) -> list[dict]:
    """Counts + response rate by source / source_quality."""
    stmt = (
        select(
            Company.source,
            Company.source_quality,
            func.count(Company.id).label("total"),
            func.sum(
                case((Company.status == RESPONDED_STATUS, 1), else_=0)
            ).label("responded"),
        )
        .where(
            Company.firm_id == firm_id,
            Company.archived_at.is_(None),
        )
        .group_by(Company.source, Company.source_quality)
        .order_by(Company.source, Company.source_quality)
    )
    if mandate_ids is not None:
        stmt = stmt.where(Company.mandate_id.in_(mandate_ids))

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "source": row.source.value if row.source else None,
            "source_quality": row.source_quality.value if row.source_quality else None,
            "total": row.total,
            "responded": int(row.responded or 0),
            "response_rate": round(int(row.responded or 0) / row.total, 4) if row.total else 0.0,
        }
        for row in rows
    ]
