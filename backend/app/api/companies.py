"""Companies router — Master List CRUD + summary envelope + cadence fields (C-01..05, X-01)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.core.deps import CurrentUser, SessionDep, visible_mandate_ids
from app.core.time import today_ist
from app.models.company import Company
from app.models.contact import Contact
from app.models.enums import (
    CompanyStatus,
    CompanyType,
    OutreachEventType,
    ScheduleStatus,
    Source,
    SourceQuality,
    StoppedReason,
)
from app.models.outreach_event import OutreachEvent
from app.models.outreach_schedule import OutreachSchedule
from app.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate
from app.schemas.outreach_schedule import OutreachScheduleUpdate
from app.services.cadence import (
    EVENT_STATUS_MAP,
    EVENT_STOP_MAP,
    activate_schedule,
    compute_cadence,
    get_followups_done,
    pause_schedule,
    resume_schedule,
    stop_schedule,
)
from app.services.cross_mandate import find_duplicates

router = APIRouter(prefix="/companies", tags=["companies"])

STOP_STATUSES = {CompanyStatus.RESPONDED, CompanyStatus.BOUNCED, CompanyStatus.DECLINED}


# ── Helpers ───────────────────────────────────────────────────────────────────


def _cadence_fields(sched: OutreachSchedule | None, followups_done: int) -> dict[str, Any]:
    """Compute next_due_date / days_remaining / is_overdue from schedule + today."""
    if sched is None or sched.status != ScheduleStatus.ACTIVE or sched.initial_date is None:
        return {
            "schedule_status": sched.status if sched else None,
            "next_due_date": None,
            "days_remaining": None,
            "is_overdue": False,
        }
    today = today_ist()
    n = followups_done + 1
    next_due = sched.initial_date + timedelta(days=n * sched.cadence_interval_days)
    days_remaining = (next_due - today).days
    return {
        "schedule_status": sched.status,
        "next_due_date": next_due.isoformat(),
        "days_remaining": days_remaining,
        "is_overdue": days_remaining < 0,
    }


async def _followups_done(db, schedule_id: int | None) -> int:
    if schedule_id is None:
        return 0
    result = await db.execute(
        select(func.count()).select_from(OutreachEvent).where(
            OutreachEvent.schedule_id == schedule_id,
            OutreachEvent.event_type == OutreachEventType.FOLLOW_UP,
        )
    )
    return result.scalar() or 0


async def _primary_contact_summary(db, company_id: int) -> dict | None:
    result = await db.execute(
        select(Contact).where(
            Contact.company_id == company_id,
            Contact.is_primary.is_(True),
            Contact.archived_at.is_(None),
        )
    )
    c = result.scalar_one_or_none()
    if not c:
        return None
    return {
        "id": c.id,
        "contact_person": c.contact_person,
        "designation": c.designation,
        "email": c.email,
    }


async def _enrich_company(db, company: Company) -> dict:
    """Return a company dict with cadence + primary-contact fields added."""
    sched_result = await db.execute(
        select(OutreachSchedule).where(OutreachSchedule.company_id == company.id)
    )
    sched = sched_result.scalar_one_or_none()

    fu_done = await _followups_done(db, sched.id if sched else None)
    cadence = _cadence_fields(sched, fu_done)
    primary = await _primary_contact_summary(db, company.id)

    base = CompanyRead.model_validate(company).model_dump()
    base.update(cadence)
    base["primary_contact"] = primary
    base["initial_date"] = sched.initial_date.isoformat() if sched and sched.initial_date else None
    return base


# ── Summary aggregate ─────────────────────────────────────────────────────────


async def _compute_summary(db, company_ids: list[int]) -> dict:
    """Compute summary stats over the entire filtered set (not just the page)."""
    if not company_ids:
        return {
            "responded_pct": 0.0,
            "overdue_count": 0,
            "needs_initial_count": 0,
            "by_status": {s.value: 0 for s in CompanyStatus},
        }

    # Status counts
    rows = await db.execute(
        select(Company.status, func.count()).where(
            Company.id.in_(company_ids)
        ).group_by(Company.status)
    )
    by_status: dict[str, int] = {s.value: 0 for s in CompanyStatus}
    total = 0
    for status_val, cnt in rows:
        by_status[status_val] = cnt
        total += cnt

    responded = by_status.get(CompanyStatus.RESPONDED.value, 0)
    responded_pct = round(responded / total, 4) if total else 0.0

    # Needs-initial count
    needs_initial = await db.execute(
        select(func.count()).select_from(OutreachSchedule).where(
            OutreachSchedule.company_id.in_(company_ids),
            OutreachSchedule.status == ScheduleStatus.AWAITING_INITIAL,
        )
    )
    needs_initial_count = needs_initial.scalar() or 0

    # Overdue count (active schedules where next_due < today)
    today = today_ist()
    active_scheds = await db.execute(
        select(OutreachSchedule).where(
            OutreachSchedule.company_id.in_(company_ids),
            OutreachSchedule.status == ScheduleStatus.ACTIVE,
            OutreachSchedule.initial_date.is_not(None),
        )
    )
    overdue_count = 0
    for sched in active_scheds.scalars().all():
        fu = await _followups_done(db, sched.id)
        n = fu + 1
        next_due = sched.initial_date + timedelta(days=n * sched.cadence_interval_days)
        if next_due < today:
            overdue_count += 1

    return {
        "responded_pct": responded_pct,
        "overdue_count": overdue_count,
        "needs_initial_count": needs_initial_count,
        "by_status": by_status,
    }


# ── Routes ────────────────────────────────────────────────────────────────────


@router.get("")
async def list_companies(
    db: SessionDep,
    current_user: CurrentUser,
    q: str | None = Query(default=None),
    status: CompanyStatus | None = Query(default=None),
    type: CompanyType | None = Query(default=None),
    bucket: str | None = Query(default=None),
    mandate_id: int | None = Query(default=None),
    source: Source | None = Query(default=None),
    sort: str | None = Query(default="company_name"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    include_archived: bool = Query(default=False),
):
    visible = await visible_mandate_ids(current_user, db)

    # Base query — firm-scoped + visibility-scoped
    base_q = select(Company).where(Company.firm_id == current_user.firm_id)
    if visible is not None:
        base_q = base_q.where(Company.mandate_id.in_(visible))
    if not include_archived:
        base_q = base_q.where(Company.archived_at.is_(None))

    # Filters
    if q:
        base_q = base_q.where(Company.company_name.ilike(f"%{q}%"))
    if status:
        base_q = base_q.where(Company.status == status)
    if type:
        base_q = base_q.where(Company.type == type)
    if bucket:
        base_q = base_q.where(Company.bucket == bucket)
    if mandate_id:
        base_q = base_q.where(Company.mandate_id == mandate_id)
    if source:
        base_q = base_q.where(Company.source == source)

    # Get all IDs for summary (before pagination)
    id_result = await db.execute(select(Company.id).where(base_q.whereclause))
    all_ids = [r[0] for r in id_result.all()]

    # Sort
    sort_col = Company.company_name
    if sort == "status":
        sort_col = Company.status
    elif sort == "created_at":
        sort_col = Company.created_at
    elif sort == "-created_at":
        sort_col = Company.created_at.desc()

    # Paginate
    total = len(all_ids)
    paged_result = await db.execute(
        base_q.order_by(sort_col).offset((page - 1) * page_size).limit(page_size)
    )
    companies = paged_result.scalars().all()

    items = [await _enrich_company(db, c) for c in companies]
    summary = await _compute_summary(db, all_ids)

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "summary": summary,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_company(body: CompanyCreate, db: SessionDep, current_user: CurrentUser):
    # Firm-scope check: mandate must belong to this firm
    from app.models.mandate import Mandate
    mandate_result = await db.execute(
        select(Mandate).where(
            Mandate.id == body.mandate_id,
            Mandate.firm_id == current_user.firm_id,
            Mandate.archived_at.is_(None),
        )
    )
    if not mandate_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Mandate not found")

    company = Company(
        firm_id=current_user.firm_id,
        created_by_id=current_user.id,
        **body.model_dump(),
    )
    db.add(company)
    await db.flush()

    # Auto-create AWAITING_INITIAL schedule (C-04)
    schedule = OutreachSchedule(
        firm_id=current_user.firm_id,
        company_id=company.id,
        status=ScheduleStatus.AWAITING_INITIAL,
    )
    db.add(schedule)
    await db.commit()

    # Cross-mandate duplicate warnings (X-01, non-blocking)
    warnings = await find_duplicates(
        db,
        firm_id=current_user.firm_id,
        mandate_id=company.mandate_id,
        company_name=company.company_name,
        website=company.website,
    )

    enriched = await _enrich_company(db, company)
    enriched["duplicate_warnings"] = warnings
    return enriched


@router.get("/check-duplicate")
async def check_duplicate(
    db: SessionDep,
    current_user: CurrentUser,
    name: str = Query(...),
    website: str | None = Query(default=None),
    mandate_id: int = Query(...),
):
    warnings = await find_duplicates(
        db,
        firm_id=current_user.firm_id,
        mandate_id=mandate_id,
        company_name=name,
        website=website,
    )
    return {"warnings": warnings}


@router.get("/{company_id}")
async def get_company(company_id: int, db: SessionDep, current_user: CurrentUser):
    visible = await visible_mandate_ids(current_user, db)

    q = select(Company).where(
        Company.id == company_id,
        Company.firm_id == current_user.firm_id,
    )
    if visible is not None:
        q = q.where(Company.mandate_id.in_(visible))

    result = await db.execute(q)
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    enriched = await _enrich_company(db, company)

    # Full contacts list
    contacts_result = await db.execute(
        select(Contact).where(
            Contact.company_id == company_id,
            Contact.archived_at.is_(None),
        )
    )
    from app.schemas.contact import ContactRead
    enriched["contacts"] = [
        ContactRead.model_validate(c).model_dump() for c in contacts_result.scalars().all()
    ]

    # Schedule detail
    sched_result = await db.execute(
        select(OutreachSchedule).where(OutreachSchedule.company_id == company_id)
    )
    sched = sched_result.scalar_one_or_none()
    if sched:
        from app.schemas.outreach_schedule import OutreachScheduleRead
        enriched["schedule"] = OutreachScheduleRead.model_validate(sched).model_dump()

    # Outreach events (newest first)
    events_result = await db.execute(
        select(OutreachEvent)
        .where(OutreachEvent.company_id == company_id)
        .order_by(OutreachEvent.occurred_on.desc(), OutreachEvent.id.desc())
    )
    from app.schemas.outreach_event import OutreachEventRead
    enriched["events"] = [
        OutreachEventRead.model_validate(e).model_dump() for e in events_result.scalars().all()
    ]

    # Cross-mandate duplicate warnings
    enriched["duplicate_warnings"] = await find_duplicates(
        db,
        firm_id=current_user.firm_id,
        mandate_id=company.mandate_id,
        company_name=company.company_name,
        website=company.website,
    )

    return enriched


@router.patch("/{company_id}")
async def update_company(
    company_id: int,
    body: CompanyUpdate,
    db: SessionDep,
    current_user: CurrentUser,
):
    visible = await visible_mandate_ids(current_user, db)
    q = select(Company).where(
        Company.id == company_id,
        Company.firm_id == current_user.firm_id,
    )
    if visible is not None:
        q = q.where(Company.mandate_id.in_(visible))

    result = await db.execute(q)
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    updates = body.model_dump(exclude_unset=True)
    for field, val in updates.items():
        setattr(company, field, val)

    # Stop schedule if status changed to RESPONDED/BOUNCED/DECLINED (C-03 + E-04)
    if "status" in updates and updates["status"] in STOP_STATUSES:
        sched_result = await db.execute(
            select(OutreachSchedule).where(OutreachSchedule.company_id == company_id)
        )
        sched = sched_result.scalar_one_or_none()
        if sched and sched.status == ScheduleStatus.ACTIVE:
            sched.status = ScheduleStatus.STOPPED
            sched.stopped_reason = StoppedReason[updates["status"].value]
            sched.stopped_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(company)
    return await _enrich_company(db, company)


@router.delete("/{company_id}", status_code=status.HTTP_200_OK)
async def archive_company(company_id: int, db: SessionDep, current_user: CurrentUser):
    """Soft-delete — sets archived_at. History is preserved."""
    visible = await visible_mandate_ids(current_user, db)
    q = select(Company).where(
        Company.id == company_id,
        Company.firm_id == current_user.firm_id,
    )
    if visible is not None:
        q = q.where(Company.mandate_id.in_(visible))

    result = await db.execute(q)
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    company.archived_at = datetime.now(timezone.utc)
    await db.commit()
    return {"detail": "Company archived"}


@router.post("/{company_id}/unarchive", status_code=status.HTTP_200_OK)
async def unarchive_company(company_id: int, db: SessionDep, current_user: CurrentUser):
    """Restore a soft-deleted company (clears archived_at)."""
    company = await _get_visible_company(company_id, db, current_user, include_archived=True)
    company.archived_at = None
    await db.commit()
    await db.refresh(company)
    return await _enrich_company(db, company)


# ── Schedule sub-resource ─────────────────────────────────────────────────────


async def _get_visible_company(
    company_id: int, db, current_user, include_archived: bool = False
):
    visible = await visible_mandate_ids(current_user, db)
    q = select(Company).where(
        Company.id == company_id,
        Company.firm_id == current_user.firm_id,
    )
    if not include_archived:
        q = q.where(Company.archived_at.is_(None))
    if visible is not None:
        q = q.where(Company.mandate_id.in_(visible))
    result = await db.execute(q)
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.get("/{company_id}/schedule")
async def get_schedule(company_id: int, db: SessionDep, current_user: CurrentUser):
    await _get_visible_company(company_id, db, current_user)
    sched_result = await db.execute(
        select(OutreachSchedule).where(OutreachSchedule.company_id == company_id)
    )
    sched = sched_result.scalar_one_or_none()
    if not sched:
        raise HTTPException(status_code=404, detail="Schedule not found")
    fu = await get_followups_done(db, sched.id)
    cadence = compute_cadence(sched, fu)
    from app.schemas.outreach_schedule import OutreachScheduleRead
    base = OutreachScheduleRead.model_validate(sched).model_dump()
    base.update(cadence)
    return base


@router.patch("/{company_id}/schedule")
async def update_schedule(
    company_id: int,
    body: OutreachScheduleUpdate,
    db: SessionDep,
    current_user: CurrentUser,
    action: str | None = Query(default=None, description="pause | resume"),
):
    await _get_visible_company(company_id, db, current_user)
    sched_result = await db.execute(
        select(OutreachSchedule).where(OutreachSchedule.company_id == company_id)
    )
    sched = sched_result.scalar_one_or_none()
    if not sched:
        raise HTTPException(status_code=404, detail="Schedule not found")

    updates = body.model_dump(exclude_unset=True)
    for field, val in updates.items():
        setattr(sched, field, val)

    if action == "pause":
        await pause_schedule(db, sched)
    elif action == "resume":
        await resume_schedule(db, sched)

    await db.commit()
    await db.refresh(sched)
    fu = await get_followups_done(db, sched.id)
    cadence = compute_cadence(sched, fu)
    from app.schemas.outreach_schedule import OutreachScheduleRead
    base = OutreachScheduleRead.model_validate(sched).model_dump()
    base.update(cadence)
    return base


# ── Events sub-resource ───────────────────────────────────────────────────────


@router.get("/{company_id}/events")
async def get_events(company_id: int, db: SessionDep, current_user: CurrentUser):
    await _get_visible_company(company_id, db, current_user, include_archived=True)
    result = await db.execute(
        select(OutreachEvent)
        .where(OutreachEvent.company_id == company_id)
        .order_by(OutreachEvent.occurred_on.desc(), OutreachEvent.id.desc())
    )
    from app.schemas.outreach_event import OutreachEventRead
    return [OutreachEventRead.model_validate(e).model_dump() for e in result.scalars().all()]


@router.post("/{company_id}/events", status_code=status.HTTP_201_CREATED)
async def log_event(
    company_id: int,
    body: "EventCreate",
    db: SessionDep,
    current_user: CurrentUser,
):
    from app.schemas.outreach_event import OutreachEventCreate
    company = await _get_visible_company(company_id, db, current_user)

    sched_result = await db.execute(
        select(OutreachSchedule).where(OutreachSchedule.company_id == company_id)
    )
    sched = sched_result.scalar_one_or_none()

    event = OutreachEvent(
        firm_id=current_user.firm_id,
        company_id=company_id,
        schedule_id=sched.id if sched else None,
        contact_id=body.contact_id,
        event_type=body.event_type,
        occurred_on=body.occurred_on,
        regarding=body.regarding,
        notes=body.notes,
        owner_id=current_user.id,
    )
    db.add(event)

    from app.models.enums import OutreachEventType
    # INITIAL_EMAIL → activate schedule (E-01)
    if body.event_type == OutreachEventType.INITIAL_EMAIL and sched:
        await activate_schedule(db, sched, body.occurred_on)

    # RESPONSE / BOUNCE → stop schedule + update company status (E-04)
    if body.event_type in EVENT_STOP_MAP and sched:
        from app.services.cadence import StoppedReason
        await stop_schedule(db, sched, EVENT_STOP_MAP[body.event_type])
        company.status = EVENT_STATUS_MAP[body.event_type]

    # Update last_contact_date on the contact if provided (L-03)
    if body.contact_id:
        from app.models.contact import Contact
        contact_result = await db.execute(
            select(Contact).where(
                Contact.id == body.contact_id,
                Contact.firm_id == current_user.firm_id,
            )
        )
        contact = contact_result.scalar_one_or_none()
        if contact:
            if contact.last_contact_date is None or body.occurred_on > contact.last_contact_date:
                contact.last_contact_date = body.occurred_on

    await db.flush()
    await db.commit()

    from app.schemas.outreach_event import OutreachEventRead
    return OutreachEventRead.model_validate(event).model_dump()


# Forward-ref for the event body — defined here to avoid circular imports
from pydantic import BaseModel as _BaseModel
from datetime import date as _date
from app.models.enums import OutreachEventType as _EventType


class EventCreate(_BaseModel):
    event_type: _EventType
    occurred_on: _date
    contact_id: int | None = None
    regarding: str | None = None
    notes: str | None = None


# ── Benchmark ─────────────────────────────────────────────────────────────────

@router.get("/{company_id}/benchmark")
async def get_benchmark(company_id: int, db: SessionDep, current_user: CurrentUser):
    """§5.4 mandate comparison — mandate avg vs this company."""
    from app.services.benchmark import get_benchmark as _get_benchmark
    await _get_visible_company(company_id, db, current_user, include_archived=True)
    return await _get_benchmark(db, company_id, current_user.firm_id)
