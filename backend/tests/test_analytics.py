"""Analytics endpoint tests (Phase 6 — A-01/A-02 + benchmark + sources)."""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mandate import Mandate
from app.models.user import User

PARTNER = {"email": "partner@test.com", "password": "Passw0rd!"}
ANALYST = {"email": "analyst@test.com", "password": "Passw0rd!"}


async def _login(client: AsyncClient, creds=None) -> None:
    resp = await client.post("/auth/login", json=creds or PARTNER)
    assert resp.status_code == 200


async def _make_company(client: AsyncClient, mandate_id: int, name: str = "Corp", **extra) -> dict:
    resp = await client.post(
        "/companies",
        json={"company_name": name, "mandate_id": mandate_id, "type": "TARGET", **extra},
    )
    assert resp.status_code == 201
    return resp.json()


async def _log_event(client: AsyncClient, company_id: int, event_type: str, occurred_on: str) -> dict:
    resp = await client.post(
        f"/companies/{company_id}/events",
        json={"event_type": event_type, "occurred_on": occurred_on},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


# ── Overview ──────────────────────────────────────────────────────────────────


async def test_overview_basic(client: AsyncClient, mandate: Mandate, partner: User):
    await _login(client)
    await _make_company(client, mandate.id, "Alpha")
    await _make_company(client, mandate.id, "Beta")

    resp = await client.get("/analytics/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert "total" in data
    assert "by_status" in data
    assert "responded_pct" in data
    assert "due_this_week" in data
    assert "overdue" in data
    assert "needs_initial" in data
    assert data["total"] >= 2


async def test_overview_needs_initial_count(client: AsyncClient, mandate: Mandate, partner: User):
    await _login(client)
    await _make_company(client, mandate.id, "Gamma")
    await _make_company(client, mandate.id, "Delta")

    resp = await client.get("/analytics/overview")
    assert resp.json()["needs_initial"] >= 2


async def test_overview_responded_pct(client: AsyncClient, mandate: Mandate, partner: User):
    await _login(client)
    c1 = await _make_company(client, mandate.id, "Resp1")
    c2 = await _make_company(client, mandate.id, "NoResp")

    # Activate c1 then log RESPONSE
    await _log_event(client, c1["id"], "INITIAL_EMAIL", "2024-01-01")
    await _log_event(client, c1["id"], "RESPONSE", "2024-01-10")

    resp = await client.get("/analytics/overview")
    data = resp.json()
    assert data["responded_pct"] > 0.0


async def test_overview_requires_auth(client: AsyncClient):
    assert (await client.get("/analytics/overview")).status_code == 401


# ── Response by bucket (A-01) ─────────────────────────────────────────────────


async def test_response_by_bucket(client: AsyncClient, mandate: Mandate, partner: User):
    await _login(client)
    await _make_company(client, mandate.id, "Bucket1", bucket="Strategic")
    await _make_company(client, mandate.id, "Bucket2", bucket="Strategic")
    await _make_company(client, mandate.id, "Bucket3", bucket="Financial")

    resp = await client.get("/analytics/response-by-bucket")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    buckets = {row["bucket"] for row in data["items"]}
    assert "Strategic" in buckets
    assert "Financial" in buckets


async def test_response_by_bucket_response_rate(client: AsyncClient, mandate: Mandate, partner: User):
    """After logging a RESPONSE, the bucket response rate > 0."""
    await _login(client)
    c = await _make_company(client, mandate.id, "RateCo", bucket="PE")
    await _log_event(client, c["id"], "INITIAL_EMAIL", "2024-01-01")
    await _log_event(client, c["id"], "RESPONSE", "2024-01-15")

    resp = await client.get("/analytics/response-by-bucket")
    pe_row = next(
        (r for r in resp.json()["items"] if r["bucket"] == "PE"), None
    )
    assert pe_row is not None
    assert pe_row["response_rate"] > 0.0


# ── By-analyst (A-02) ────────────────────────────────────────────────────────


async def test_by_analyst_partner_200(client: AsyncClient, mandate: Mandate, partner: User):
    await _login(client)
    resp = await client.get("/analytics/by-analyst")
    assert resp.status_code == 200
    assert "items" in resp.json()


async def test_by_analyst_analyst_403(
    client: AsyncClient, mandate: Mandate, partner: User, analyst: User
):
    await _login(client, ANALYST)
    resp = await client.get("/analytics/by-analyst")
    assert resp.status_code == 403


async def test_by_analyst_counts_events(client: AsyncClient, mandate: Mandate, partner: User):
    await _login(client)
    c = await _make_company(client, mandate.id, "AnalystTest")
    await _log_event(client, c["id"], "INITIAL_EMAIL", "2024-01-01")
    await _log_event(client, c["id"], "FOLLOW_UP", "2024-01-15")

    resp = await client.get("/analytics/by-analyst")
    partner_row = next(
        (r for r in resp.json()["items"] if r["user_id"] == partner.id), None
    )
    assert partner_row is not None
    assert partner_row["total_events"] >= 2
    assert partner_row["initial_emails"] >= 1


# ── Sources ───────────────────────────────────────────────────────────────────


async def test_sources_endpoint(client: AsyncClient, mandate: Mandate, partner: User):
    await _login(client)
    await _make_company(client, mandate.id, "SrcProp")

    resp = await client.get("/analytics/sources")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert len(data["items"]) >= 1
    row = data["items"][0]
    assert "source" in row
    assert "source_quality" in row
    assert "total" in row
    assert "response_rate" in row


# ── Benchmark ────────────────────────────────────────────────────────────────


async def test_benchmark_endpoint(client: AsyncClient, mandate: Mandate, partner: User):
    await _login(client)
    c1 = await _make_company(client, mandate.id, "Bench1")
    c2 = await _make_company(client, mandate.id, "Bench2")

    # Respond c2 so mandate has a responded company
    await _log_event(client, c2["id"], "INITIAL_EMAIL", "2024-01-01")
    await _log_event(client, c2["id"], "RESPONSE", "2024-01-14")

    # Touch c1 once
    await _log_event(client, c1["id"], "INITIAL_EMAIL", "2024-01-05")

    resp = await client.get(f"/companies/{c1['id']}/benchmark")
    assert resp.status_code == 200
    data = resp.json()
    assert "mandate_response_rate" in data
    assert "mandate_avg_touches_to_response" in data
    assert "mandate_avg_days_to_response" in data
    assert "this_company_touches" in data
    assert data["mandate_response_rate"] > 0.0
    assert data["this_company_touches"] >= 1


async def test_benchmark_not_found(client: AsyncClient, partner: User):
    await _login(client)
    resp = await client.get("/companies/99999/benchmark")
    assert resp.status_code == 404
