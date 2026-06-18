"""Company endpoint tests — CRUD, filters, summary envelope, soft-delete, duplicate detection."""

from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.mandate import Mandate
from app.models.mandate_assignment import MandateAssignment
from app.models.outreach_schedule import OutreachSchedule
from app.models.enums import CompanyStatus, CompanyType, MandateStatus, MandateType, ScheduleStatus, Source
from app.models.firm import Firm
from app.models.user import User
from app.core.security import hash_password
from app.models.enums import UserRole

PARTNER_CREDS = {"email": "partner@test.com", "password": "Passw0rd!"}
ANALYST_CREDS = {"email": "analyst@test.com", "password": "Passw0rd!"}


async def _login(client: AsyncClient, creds: dict) -> None:
    resp = await client.post("/auth/login", json=creds)
    assert resp.status_code == 200


async def _create_company(client: AsyncClient, mandate_id: int, name: str = "Test Corp", **kwargs) -> dict:
    payload = {
        "company_name": name,
        "mandate_id": mandate_id,
        "type": "TARGET",
        "website": f"https://www.{name.lower().replace(' ', '')}.com",
        **kwargs,
    }
    resp = await client.post("/companies", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def second_mandate(db_session: AsyncSession, firm: Firm, partner: User) -> Mandate:
    m = Mandate(
        firm_id=firm.id,
        client_name="Client B",
        name="Mandate B",
        type=MandateType.BUY_SIDE,
        status=MandateStatus.ACTIVE,
        lead_owner_id=partner.id,
    )
    db_session.add(m)
    await db_session.commit()
    await db_session.refresh(m)
    return m


# ── Company CRUD ──────────────────────────────────────────────────────────────


async def test_create_company_201(client: AsyncClient, mandate: Mandate, partner: User):
    await _login(client, PARTNER_CREDS)
    data = await _create_company(client, mandate.id)

    assert data["company_name"] == "Test Corp"
    assert data["firm_id"] == partner.firm_id
    assert data["status"] == "NOT_CONTACTED"
    # Auto-created AWAITING_INITIAL schedule
    assert data["schedule_status"] == "AWAITING_INITIAL"
    assert data["initial_date"] is None
    assert data["next_due_date"] is None


async def test_create_company_auto_creates_schedule(
    client: AsyncClient, db_session: AsyncSession, mandate: Mandate, partner: User
):
    await _login(client, PARTNER_CREDS)
    data = await _create_company(client, mandate.id)

    from sqlalchemy import select
    sched = await db_session.execute(
        select(OutreachSchedule).where(OutreachSchedule.company_id == data["id"])
    )
    assert sched.scalar_one_or_none() is not None


async def test_create_company_cross_mandate_warning(
    client: AsyncClient, mandate: Mandate, second_mandate: Mandate, partner: User
):
    """Same name in two mandates triggers an X-01 advisory warning."""
    await _login(client, PARTNER_CREDS)
    await _create_company(client, mandate.id, name="Acme Corp", website="https://acme.com")

    # Create duplicate in second mandate
    resp2 = await client.post(
        "/companies",
        json={"company_name": "Acme Corp", "mandate_id": second_mandate.id, "type": "TARGET"},
    )
    assert resp2.status_code == 201
    assert len(resp2.json()["duplicate_warnings"]) >= 1


async def test_get_company(client: AsyncClient, mandate: Mandate, partner: User):
    await _login(client, PARTNER_CREDS)
    created = await _create_company(client, mandate.id)
    resp = await client.get(f"/companies/{created['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == created["id"]
    assert "contacts" in data
    assert "events" in data


async def test_get_company_not_found(client: AsyncClient, partner: User):
    await _login(client, PARTNER_CREDS)
    resp = await client.get("/companies/99999")
    assert resp.status_code == 404


async def test_update_company(client: AsyncClient, mandate: Mandate, partner: User):
    await _login(client, PARTNER_CREDS)
    created = await _create_company(client, mandate.id)
    resp = await client.patch(f"/companies/{created['id']}", json={"hq": "Mumbai", "headcount": 500})
    assert resp.status_code == 200
    assert resp.json()["hq"] == "Mumbai"
    assert resp.json()["headcount"] == 500


async def test_update_status_to_responded_stops_schedule(
    client: AsyncClient, db_session: AsyncSession, mandate: Mandate, partner: User
):
    """PATCH status=RESPONDED → schedule becomes STOPPED (E-04)."""
    await _login(client, PARTNER_CREDS)
    created = await _create_company(client, mandate.id)

    # Manually activate the schedule so it can be stopped
    from sqlalchemy import select
    sched = (await db_session.execute(
        select(OutreachSchedule).where(OutreachSchedule.company_id == created["id"])
    )).scalar_one()
    from datetime import date
    sched.status = ScheduleStatus.ACTIVE
    sched.initial_date = date(2024, 1, 1)
    await db_session.commit()

    resp = await client.patch(f"/companies/{created['id']}", json={"status": "RESPONDED"})
    assert resp.status_code == 200

    await db_session.refresh(sched)
    assert sched.status == ScheduleStatus.STOPPED


async def test_soft_delete_company(
    client: AsyncClient, db_session: AsyncSession, mandate: Mandate, partner: User
):
    await _login(client, PARTNER_CREDS)
    created = await _create_company(client, mandate.id)
    cid = created["id"]

    # Archive
    del_resp = await client.delete(f"/companies/{cid}")
    assert del_resp.status_code == 200

    # Not visible without include_archived
    list_resp = await client.get("/companies")
    ids = [c["id"] for c in list_resp.json()["items"]]
    assert cid not in ids

    # Visible with include_archived
    list_resp2 = await client.get("/companies?include_archived=true")
    ids2 = [c["id"] for c in list_resp2.json()["items"]]
    assert cid in ids2

    # History preserved in DB
    from sqlalchemy import select
    company = (await db_session.execute(select(Company).where(Company.id == cid))).scalar_one()
    assert company.archived_at is not None


async def test_unarchive_company_restores(
    client: AsyncClient, db_session: AsyncSession, mandate: Mandate, partner: User
):
    await _login(client, PARTNER_CREDS)
    created = await _create_company(client, mandate.id, name="Restore Me")
    cid = created["id"]

    await client.delete(f"/companies/{cid}")
    # Restore
    restore = await client.post(f"/companies/{cid}/unarchive")
    assert restore.status_code == 200
    assert restore.json()["archived_at"] is None

    # Back in the default list
    list_resp = await client.get("/companies")
    assert cid in [c["id"] for c in list_resp.json()["items"]]


# ── List filters + summary ────────────────────────────────────────────────────


async def test_list_companies_requires_auth(client: AsyncClient):
    resp = await client.get("/companies")
    assert resp.status_code == 401


async def test_list_companies_returns_envelope(
    client: AsyncClient, mandate: Mandate, partner: User
):
    await _login(client, PARTNER_CREDS)
    await _create_company(client, mandate.id, name="Alpha Co")
    await _create_company(client, mandate.id, name="Beta Co")

    resp = await client.get("/companies")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data and "total" in data and "summary" in data
    assert data["total"] >= 2
    assert "responded_pct" in data["summary"]
    assert "by_status" in data["summary"]
    assert "needs_initial_count" in data["summary"]


async def test_list_filter_by_status(client: AsyncClient, mandate: Mandate, partner: User):
    await _login(client, PARTNER_CREDS)
    await _create_company(client, mandate.id, name="Acme A")
    c2 = await _create_company(client, mandate.id, name="Acme B")
    await client.patch(f"/companies/{c2['id']}", json={"status": "INTERESTED"})

    resp = await client.get("/companies?status=INTERESTED")
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert all(i["status"] == "INTERESTED" for i in items)


async def test_list_search_by_name(client: AsyncClient, mandate: Mandate, partner: User):
    await _login(client, PARTNER_CREDS)
    await _create_company(client, mandate.id, name="Tata Steel")
    await _create_company(client, mandate.id, name="Infosys")

    resp = await client.get("/companies?q=tata")
    items = resp.json()["items"]
    assert all("tata" in i["company_name"].lower() for i in items)
    assert all("infosys" not in i["company_name"].lower() for i in items)


async def test_summary_reflects_full_filtered_set(
    client: AsyncClient, mandate: Mandate, partner: User
):
    """Summary aggregates are computed over the whole filtered set, not just one page."""
    await _login(client, PARTNER_CREDS)
    for i in range(5):
        await _create_company(client, mandate.id, name=f"Company {i}")

    # Request page 1 with page_size=2 — summary should still reflect all 5
    resp = await client.get("/companies?page=1&page_size=2")
    data = resp.json()
    assert data["total"] >= 5
    assert data["page_size"] == 2
    assert len(data["items"]) == 2
    # needs_initial_count covers all, not just the 2 on this page
    assert data["summary"]["needs_initial_count"] >= 5


# ── Firm scoping (analyst) ────────────────────────────────────────────────────


async def test_analyst_only_sees_assigned_mandate_companies(
    client: AsyncClient,
    db_session: AsyncSession,
    firm: Firm,
    mandate: Mandate,
    second_mandate: Mandate,
    analyst: User,
    partner: User,
):
    """Analyst assigned to mandate only; should NOT see second_mandate companies."""
    # Assign analyst to first mandate only
    db_session.add(MandateAssignment(mandate_id=mandate.id, user_id=analyst.id))
    await db_session.commit()

    # Create one company in each mandate (as partner)
    await _login(client, PARTNER_CREDS)
    c1 = await _create_company(client, mandate.id, name="Visible Co")
    c2 = await _create_company(client, second_mandate.id, name="Hidden Co")

    # Login as analyst
    await _login(client, ANALYST_CREDS)
    resp = await client.get("/companies")
    ids = [c["id"] for c in resp.json()["items"]]
    assert c1["id"] in ids
    assert c2["id"] not in ids


# ── Check-duplicate endpoint ──────────────────────────────────────────────────


async def test_check_duplicate_endpoint(
    client: AsyncClient, mandate: Mandate, second_mandate: Mandate, partner: User
):
    await _login(client, PARTNER_CREDS)
    await _create_company(client, mandate.id, name="Wipro Ltd", website="https://wipro.com")

    resp = await client.get(
        f"/companies/check-duplicate?name=Wipro+Ltd&mandate_id={second_mandate.id}"
    )
    assert resp.status_code == 200
    assert len(resp.json()["warnings"]) >= 1
