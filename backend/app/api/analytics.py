"""Analytics API — overview, response-by-bucket, by-analyst, sources (§6.5)."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.deps import CurrentUser, PartnerDep, SessionDep, visible_mandate_ids
from app.services import analytics as svc

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
async def analytics_overview(db: SessionDep, current_user: CurrentUser):
    """KPI overview: totals, by-status, % responded, due-this-week, overdue, needs-initial."""
    mandate_ids = await visible_mandate_ids(current_user, db)
    return await svc.get_overview(db, current_user.firm_id, mandate_ids)


@router.get("/response-by-bucket")
async def response_by_bucket(db: SessionDep, current_user: CurrentUser):
    """Response rate grouped by bucket (A-01)."""
    mandate_ids = await visible_mandate_ids(current_user, db)
    return {"items": await svc.get_response_by_bucket(db, current_user.firm_id, mandate_ids)}


@router.get("/by-analyst")
async def by_analyst(db: SessionDep, current_user: PartnerDep):
    """Volume / responses / conversion per analyst — partner only (A-02)."""
    return {"items": await svc.get_by_analyst(db, current_user.firm_id)}


@router.get("/sources")
async def sources(db: SessionDep, current_user: CurrentUser):
    """Counts + response rate by source / source_quality."""
    mandate_ids = await visible_mandate_ids(current_user, db)
    return {"items": await svc.get_sources(db, current_user.firm_id, mandate_ids)}
