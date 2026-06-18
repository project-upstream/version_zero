"""Schedule work-queue routes — the analyst's daily driver (E-05, E-07, §6.3)."""

from __future__ import annotations

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from app.core.deps import CurrentUser, SessionDep, visible_mandate_ids
from app.core.time import today_ist
from app.models.company import Company
from app.models.enums import OutreachEventType, ScheduleStatus, UserRole
from app.models.outreach_event import OutreachEvent
from app.models.outreach_schedule import OutreachSchedule
from app.services.cadence import compute_cadence, get_followups_done
from app.schemas.outreach_schedule import OutreachScheduleRead

router = APIRouter(prefix="/schedule", tags=["schedule"])


async def _enrich_row(db, sched: OutreachSchedule, company: Company) -> dict:
    """Build a work-queue row: company summary + schedule + cadence computed fields."""
    fu = await get_followups_done(db, sched.id)
    cadence = compute_cadence(sched, fu)
    return {
        "company_id": company.id,
        "company_name": company.company_name,
        "mandate_id": company.mandate_id,
        "company_status": company.status,
        "schedule_id": sched.id,
        "cadence_interval_days": sched.cadence_interval_days,
        "regarding": sched.regarding,
        **cadence,
    }


async def _last_event_date(db, company_id: int) -> str | None:
    result = await db.execute(
        select(OutreachEvent.occurred_on)
        .where(OutreachEvent.company_id == company_id)
        .order_by(OutreachEvent.occurred_on.desc())
        .limit(1)
    )
    row = result.scalar_one_or_none()
    return row.isoformat() if row else None


@router.get("/needs-initial")
async def needs_initial(db: SessionDep, current_user: CurrentUser):
    """Companies whose outreach schedule is AWAITING_INITIAL (E-07)."""
    visible = await visible_mandate_ids(current_user, db)

    q = (
        select(OutreachSchedule, Company)
        .join(Company, Company.id == OutreachSchedule.company_id)
        .where(
            OutreachSchedule.status == ScheduleStatus.AWAITING_INITIAL,
            Company.firm_id == current_user.firm_id,
            Company.archived_at.is_(None),
        )
    )
    if visible is not None:
        q = q.where(Company.mandate_id.in_(visible))

    rows = (await db.execute(q)).all()
    items = []
    for sched, company in rows:
        row = await _enrich_row(db, sched, company)
        row["last_event_date"] = await _last_event_date(db, company.id)
        items.append(row)

    return {"items": items, "total": len(items)}


@router.get("/due")
async def due(
    db: SessionDep,
    current_user: CurrentUser,
    window: int = Query(default=7, ge=1, le=90),
):
    """Active schedules due within the window (overdue first) — analyst's work queue (E-07)."""
    visible = await visible_mandate_ids(current_user, db)
    today = today_ist()

    q = (
        select(OutreachSchedule, Company)
        .join(Company, Company.id == OutreachSchedule.company_id)
        .where(
            OutreachSchedule.status == ScheduleStatus.ACTIVE,
            OutreachSchedule.initial_date.is_not(None),
            Company.firm_id == current_user.firm_id,
            Company.archived_at.is_(None),
        )
    )
    if visible is not None:
        q = q.where(Company.mandate_id.in_(visible))

    rows = (await db.execute(q)).all()
    items = []
    for sched, company in rows:
        fu = await get_followups_done(db, sched.id)
        cadence = compute_cadence(sched, fu)
        days_remaining = cadence["days_remaining"]
        if days_remaining is None or days_remaining > window:
            continue
        row = {
            "company_id": company.id,
            "company_name": company.company_name,
            "mandate_id": company.mandate_id,
            "company_status": company.status,
            "schedule_id": sched.id,
            "cadence_interval_days": sched.cadence_interval_days,
            "regarding": sched.regarding,
            **cadence,
            "last_event_date": await _last_event_date(db, company.id),
        }
        items.append(row)

    # Overdue first (most negative days_remaining first), then by next_due asc
    items.sort(key=lambda r: (r["days_remaining"] or 0))
    return {"items": items, "total": len(items)}


@router.get("/overdue")
async def overdue(db: SessionDep, current_user: CurrentUser):
    """All overdue schedules — partner escalation view (E-05)."""
    visible = await visible_mandate_ids(current_user, db)

    q = (
        select(OutreachSchedule, Company)
        .join(Company, Company.id == OutreachSchedule.company_id)
        .where(
            OutreachSchedule.status == ScheduleStatus.ACTIVE,
            OutreachSchedule.initial_date.is_not(None),
            Company.firm_id == current_user.firm_id,
            Company.archived_at.is_(None),
        )
    )
    if visible is not None:
        q = q.where(Company.mandate_id.in_(visible))

    rows = (await db.execute(q)).all()
    today = today_ist()
    items = []
    for sched, company in rows:
        fu = await get_followups_done(db, sched.id)
        cadence = compute_cadence(sched, fu)
        if not cadence.get("is_overdue"):
            continue
        items.append({
            "company_id": company.id,
            "company_name": company.company_name,
            "mandate_id": company.mandate_id,
            "company_status": company.status,
            "schedule_id": sched.id,
            **cadence,
            "last_event_date": await _last_event_date(db, company.id),
        })

    items.sort(key=lambda r: r["days_remaining"] or 0)
    return {"items": items, "total": len(items)}


@router.get("/stats")
async def schedule_stats(db: SessionDep, current_user: CurrentUser):
    """Email stats panel: sent/responses this week, response rate, overdue count."""
    visible = await visible_mandate_ids(current_user, db)
    today = today_ist()

    # Week boundaries (Mon–Sun IST)
    week_start = today.replace(day=today.day - today.weekday())
    from datetime import timedelta
    week_end = week_start + timedelta(days=6)

    # Base event query for this firm (+ visibility scope)
    event_base = (
        select(OutreachEvent)
        .join(Company, Company.id == OutreachEvent.company_id)
        .where(
            OutreachEvent.firm_id == current_user.firm_id,
        )
    )
    if visible is not None:
        event_base = event_base.where(Company.mandate_id.in_(visible))

    # Sent this week = INITIAL_EMAIL + FOLLOW_UP this week
    sent_q = event_base.where(
        OutreachEvent.event_type.in_([
            OutreachEventType.INITIAL_EMAIL,
            OutreachEventType.FOLLOW_UP,
        ]),
        OutreachEvent.occurred_on >= week_start,
        OutreachEvent.occurred_on <= week_end,
    )
    sent_count_q = select(func.count()).select_from(sent_q.subquery())
    sent_this_week = (await db.execute(sent_count_q)).scalar() or 0

    # Responses this week
    resp_q = event_base.where(
        OutreachEvent.event_type == OutreachEventType.RESPONSE,
        OutreachEvent.occurred_on >= week_start,
        OutreachEvent.occurred_on <= week_end,
    )
    resp_count_q = select(func.count()).select_from(resp_q.subquery())
    responses_this_week = (await db.execute(resp_count_q)).scalar() or 0

    # Overall response rate (responded companies / total visible non-archived)
    company_base = select(Company).where(
        Company.firm_id == current_user.firm_id,
        Company.archived_at.is_(None),
    )
    if visible is not None:
        company_base = company_base.where(Company.mandate_id.in_(visible))

    total_q = select(func.count()).select_from(company_base.subquery())
    total = (await db.execute(total_q)).scalar() or 0

    from app.models.enums import CompanyStatus
    resp_co_q = select(func.count()).select_from(
        company_base.where(Company.status == CompanyStatus.RESPONDED).subquery()
    )
    responded = (await db.execute(resp_co_q)).scalar() or 0
    response_rate = round(responded / total, 4) if total else 0.0

    # Overdue count
    sched_q = (
        select(OutreachSchedule, Company)
        .join(Company, Company.id == OutreachSchedule.company_id)
        .where(
            OutreachSchedule.status == ScheduleStatus.ACTIVE,
            OutreachSchedule.initial_date.is_not(None),
            Company.firm_id == current_user.firm_id,
            Company.archived_at.is_(None),
        )
    )
    if visible is not None:
        sched_q = sched_q.where(Company.mandate_id.in_(visible))

    overdue_count = 0
    for sched, company in (await db.execute(sched_q)).all():
        fu = await get_followups_done(db, sched.id)
        cadence = compute_cadence(sched, fu)
        if cadence.get("is_overdue"):
            overdue_count += 1

    return {
        "sent_this_week": sent_this_week,
        "responses_this_week": responses_this_week,
        "response_rate": response_rate,
        "overdue_count": overdue_count,
    }
