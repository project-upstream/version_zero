"""Contact endpoint tests — CRUD, primary toggling, touch history, soft delete, firm scope."""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.contact import Contact
from app.models.mandate import Mandate
from app.models.firm import Firm
from app.models.user import User
from app.models.outreach_event import OutreachEvent
from app.models.enums import OutreachEventType

PARTNER = {"email": "partner@test.com", "password": "Passw0rd!"}


async def _login(client: AsyncClient) -> None:
    resp = await client.post("/auth/login", json=PARTNER)
    assert resp.status_code == 200


async def _make_company(client: AsyncClient, mandate_id: int, name: str = "TestCo") -> dict:
    resp = await client.post(
        "/companies",
        json={"company_name": name, "mandate_id": mandate_id, "type": "TARGET"},
    )
    assert resp.status_code == 201
    return resp.json()


async def _make_contact(
    client: AsyncClient,
    company_id: int,
    name: str = "Alice",
    is_primary: bool = False,
    **extra,
) -> dict:
    resp = await client.post(
        "/contacts",
        json={"company_id": company_id, "contact_person": name, "is_primary": is_primary, **extra},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


# ── CRUD ──────────────────────────────────────────────────────────────────────


async def test_create_contact_201(client: AsyncClient, mandate: Mandate, partner: User):
    await _login(client)
    company = await _make_company(client, mandate.id)
    contact = await _make_contact(
        client,
        company["id"],
        name="Bob Smith",
        designation="CFO",
        email="bob@example.com",
        engagement="BUY_SIDE",
    )
    assert contact["contact_person"] == "Bob Smith"
    assert contact["firm_id"] == partner.firm_id
    assert contact["designation"] == "CFO"
    assert contact["engagement"] == "BUY_SIDE"


async def test_get_contact(client: AsyncClient, mandate: Mandate, partner: User):
    await _login(client)
    company = await _make_company(client, mandate.id)
    created = await _make_contact(client, company["id"])
    resp = await client.get(f"/contacts/{created['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == created["id"]
    assert "events" in data  # touch history


async def test_get_contact_not_found(client: AsyncClient, partner: User):
    await _login(client)
    assert (await client.get("/contacts/99999")).status_code == 404


async def test_update_contact(client: AsyncClient, mandate: Mandate, partner: User):
    await _login(client)
    company = await _make_company(client, mandate.id)
    contact = await _make_contact(client, company["id"])
    resp = await client.patch(
        f"/contacts/{contact['id']}", json={"designation": "CEO", "remark": "Key decision maker"}
    )
    assert resp.status_code == 200
    assert resp.json()["designation"] == "CEO"
    assert resp.json()["remark"] == "Key decision maker"


async def test_list_contacts(client: AsyncClient, mandate: Mandate, partner: User):
    await _login(client)
    company = await _make_company(client, mandate.id)
    await _make_contact(client, company["id"], name="Alice")
    await _make_contact(client, company["id"], name="Bob")
    resp = await client.get("/contacts")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data and "total" in data
    assert data["total"] >= 2


async def test_list_filter_by_company(client: AsyncClient, mandate: Mandate, partner: User):
    await _login(client)
    co1 = await _make_company(client, mandate.id, "Co One")
    co2 = await _make_company(client, mandate.id, "Co Two")
    c1 = await _make_contact(client, co1["id"], "Alice")
    c2 = await _make_contact(client, co2["id"], "Bob")
    resp = await client.get(f"/contacts?company_id={co1['id']}")
    ids = [c["id"] for c in resp.json()["items"]]
    assert c1["id"] in ids
    assert c2["id"] not in ids


async def test_list_search_by_name(client: AsyncClient, mandate: Mandate, partner: User):
    await _login(client)
    company = await _make_company(client, mandate.id)
    await _make_contact(client, company["id"], "Rajesh Kumar")
    await _make_contact(client, company["id"], "Priya Mehta")
    resp = await client.get("/contacts?q=rajesh")
    names = [c["contact_person"] for c in resp.json()["items"]]
    assert all("rajesh" in n.lower() for n in names)
    assert not any("priya" in n.lower() for n in names)


# ── Primary contact toggling (L-01) ──────────────────────────────────────────


async def test_primary_toggling_exclusive_per_company(
    client: AsyncClient, db_session: AsyncSession, mandate: Mandate, partner: User
):
    """Setting a new primary contact unsets the previous one (≤1 per company)."""
    await _login(client)
    company = await _make_company(client, mandate.id)
    c1 = await _make_contact(client, company["id"], "First", is_primary=True)
    c2 = await _make_contact(client, company["id"], "Second", is_primary=False)

    # Set c2 as primary
    await client.patch(f"/contacts/{c2['id']}", json={"is_primary": True})

    # c1 should no longer be primary
    c1_row = (await db_session.execute(
        select(Contact).where(Contact.id == c1["id"])
    )).scalar_one()
    c2_row = (await db_session.execute(
        select(Contact).where(Contact.id == c2["id"])
    )).scalar_one()
    assert c1_row.is_primary is False
    assert c2_row.is_primary is True


async def test_create_primary_unsets_existing(
    client: AsyncClient, db_session: AsyncSession, mandate: Mandate, partner: User
):
    """Creating a new primary contact unsets the existing primary."""
    await _login(client)
    company = await _make_company(client, mandate.id)
    c1 = await _make_contact(client, company["id"], "Original", is_primary=True)

    # Create a second contact as primary
    c2 = await _make_contact(client, company["id"], "New Primary", is_primary=True)

    c1_row = (await db_session.execute(
        select(Contact).where(Contact.id == c1["id"])
    )).scalar_one()
    assert c1_row.is_primary is False


async def test_primary_reflected_on_company_list(
    client: AsyncClient, mandate: Mandate, partner: User
):
    """The company list shows the primary contact correctly after toggling."""
    await _login(client)
    company = await _make_company(client, mandate.id, "PrimaryTest Corp")
    c1 = await _make_contact(client, company["id"], "Alpha Contact", is_primary=True)

    resp = await client.get("/companies")
    company_row = next(
        (c for c in resp.json()["items"] if c["id"] == company["id"]), None
    )
    assert company_row is not None
    assert company_row["primary_contact"]["contact_person"] == "Alpha Contact"


# ── Touch history (L-03) ──────────────────────────────────────────────────────


async def test_touch_history_on_contact(
    client: AsyncClient, db_session: AsyncSession, mandate: Mandate, partner: User
):
    """GET /contacts/{id} returns chronological touch history from outreach_events."""
    await _login(client)
    company = await _make_company(client, mandate.id)
    contact = await _make_contact(client, company["id"], "Traceable Person")

    # Log two events against this contact
    await client.post(
        f"/companies/{company['id']}/events",
        json={
            "event_type": "INITIAL_EMAIL",
            "occurred_on": "2024-01-01",
            "contact_id": contact["id"],
        },
    )
    await client.post(
        f"/companies/{company['id']}/events",
        json={
            "event_type": "FOLLOW_UP",
            "occurred_on": "2024-01-15",
            "contact_id": contact["id"],
            "notes": "Called about acquisition",
        },
    )

    resp = await client.get(f"/contacts/{contact['id']}")
    events = resp.json()["events"]
    assert len(events) == 2
    # Chronological order: oldest first
    assert events[0]["occurred_on"] == "2024-01-01"
    assert events[1]["occurred_on"] == "2024-01-15"
    assert events[1]["notes"] == "Called about acquisition"


async def test_last_contact_date_updated_on_event(
    client: AsyncClient, db_session: AsyncSession, mandate: Mandate, partner: User
):
    """Logging an event with contact_id updates contact.last_contact_date (L-03)."""
    await _login(client)
    company = await _make_company(client, mandate.id)
    contact = await _make_contact(client, company["id"])

    await client.post(
        f"/companies/{company['id']}/events",
        json={
            "event_type": "CALL",
            "occurred_on": "2024-03-15",
            "contact_id": contact["id"],
        },
    )

    contact_row = (await db_session.execute(
        select(Contact).where(Contact.id == contact["id"])
    )).scalar_one()
    from datetime import date
    assert contact_row.last_contact_date == date(2024, 3, 15)


# ── Soft delete ───────────────────────────────────────────────────────────────


async def test_soft_delete_contact(
    client: AsyncClient, db_session: AsyncSession, mandate: Mandate, partner: User
):
    await _login(client)
    company = await _make_company(client, mandate.id)
    contact = await _make_contact(client, company["id"])
    cid = contact["id"]

    del_resp = await client.delete(f"/contacts/{cid}")
    assert del_resp.status_code == 200

    # Not in default list
    list_resp = await client.get("/contacts")
    ids = [c["id"] for c in list_resp.json()["items"]]
    assert cid not in ids

    # Visible with include_archived
    archived_resp = await client.get("/contacts?include_archived=true")
    ids2 = [c["id"] for c in archived_resp.json()["items"]]
    assert cid in ids2

    # DB row preserved
    row = (await db_session.execute(select(Contact).where(Contact.id == cid))).scalar_one()
    assert row.archived_at is not None


async def test_unarchive_contact_restores(
    client: AsyncClient, db_session: AsyncSession, mandate: Mandate, partner: User
):
    await _login(client)
    company = await _make_company(client, mandate.id)
    contact = await _make_contact(client, company["id"])
    cid = contact["id"]

    await client.delete(f"/contacts/{cid}")
    restore = await client.post(f"/contacts/{cid}/unarchive")
    assert restore.status_code == 200
    assert restore.json()["archived_at"] is None

    # Back in default list
    list_resp = await client.get("/contacts")
    assert cid in [c["id"] for c in list_resp.json()["items"]]


# ── Requires auth ─────────────────────────────────────────────────────────────


async def test_contacts_requires_auth(client: AsyncClient):
    assert (await client.get("/contacts")).status_code == 401
