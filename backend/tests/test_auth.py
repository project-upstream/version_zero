"""Auth endpoint tests — signup, login, /me, refresh rotation, logout, firm scoping."""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import visible_mandate_ids
from app.models.firm import Firm
from app.models.user import User

CREDS = {"email": "partner@test.com", "password": "Passw0rd!"}
ANALYST_CREDS = {"email": "analyst@test.com", "password": "Passw0rd!"}


# ── Signup ────────────────────────────────────────────────────────────────────


async def test_signup_creates_firm_and_partner(client: AsyncClient):
    resp = await client.post(
        "/auth/signup",
        json={"firm_name": "Apex Capital", "full_name": "Alice CEO", "email": "alice@apex.com", "password": "Secret1!"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["role"] == "PARTNER"
    assert data["firm"]["name"] == "Apex Capital"
    assert "hashed_password" not in data
    assert settings.access_cookie_name in resp.cookies
    assert settings.refresh_cookie_name in resp.cookies


async def test_signup_duplicate_email(client: AsyncClient, partner: User):
    resp = await client.post(
        "/auth/signup",
        json={"firm_name": "Other Firm", "full_name": "Bob", "email": CREDS["email"], "password": "Secret1!"},
    )
    assert resp.status_code == 409


# ── Login ─────────────────────────────────────────────────────────────────────


async def test_login_success(client: AsyncClient, partner: User):
    resp = await client.post("/auth/login", json=CREDS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == CREDS["email"]
    assert data["role"] == "PARTNER"
    assert "hashed_password" not in data
    assert settings.access_cookie_name in resp.cookies
    assert settings.refresh_cookie_name in resp.cookies


async def test_login_wrong_password(client: AsyncClient, partner: User):
    resp = await client.post("/auth/login", json={**CREDS, "password": "wrongpass"})
    assert resp.status_code == 401


async def test_login_unknown_email(client: AsyncClient):
    resp = await client.post("/auth/login", json={"email": "nobody@nowhere.com", "password": "x"})
    assert resp.status_code == 401


# ── /auth/me ─────────────────────────────────────────────────────────────────


async def test_me_ok(client: AsyncClient, partner: User):
    await client.post("/auth/login", json=CREDS)
    resp = await client.get("/auth/me")
    assert resp.status_code == 200
    assert resp.json()["email"] == CREDS["email"]
    assert resp.json()["firm"]["name"] == "Test Firm"


async def test_me_no_cookie_401(client: AsyncClient):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


async def test_me_invalid_cookie_401(client: AsyncClient):
    client.cookies.set(settings.access_cookie_name, "not.a.valid.jwt")
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


# ── Refresh rotation ──────────────────────────────────────────────────────────


async def test_refresh_rotates_token(client: AsyncClient, partner: User):
    login_resp = await client.post("/auth/login", json=CREDS)
    old_refresh = login_resp.cookies[settings.refresh_cookie_name]

    refresh_resp = await client.post("/auth/refresh")
    assert refresh_resp.status_code == 200
    new_refresh = refresh_resp.cookies.get(settings.refresh_cookie_name)
    assert new_refresh is not None
    assert new_refresh != old_refresh


async def test_refresh_old_token_rejected(client: AsyncClient, partner: User):
    """After rotating, the old refresh token must be revoked."""
    await client.post("/auth/login", json=CREDS)
    old_refresh = client.cookies.get(settings.refresh_cookie_name)

    # First refresh — consumes old token, sets new one in client cookie jar
    await client.post("/auth/refresh")

    # Manually set old refresh cookie back and try again
    client.cookies.set(settings.refresh_cookie_name, old_refresh)
    resp = await client.post("/auth/refresh")
    assert resp.status_code == 401


async def test_refresh_no_cookie_401(client: AsyncClient):
    resp = await client.post("/auth/refresh")
    assert resp.status_code == 401


# ── Token version (revoke all sessions) ──────────────────────────────────────


async def test_token_version_bump_invalidates_session(
    client: AsyncClient, db_session: AsyncSession, partner: User
):
    await client.post("/auth/login", json=CREDS)
    # Verify access works
    assert (await client.get("/auth/me")).status_code == 200

    # Bump token_version server-side (simulates "log out everywhere")
    partner.token_version += 1
    await db_session.commit()

    # Existing access cookie now carries the old version → 401
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


# ── Logout ────────────────────────────────────────────────────────────────────


async def test_logout_clears_session(client: AsyncClient, partner: User):
    await client.post("/auth/login", json=CREDS)
    assert (await client.get("/auth/me")).status_code == 200

    logout_resp = await client.post("/auth/logout")
    assert logout_resp.status_code == 200

    # Cookies should be cleared; /me should fail
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


async def test_logout_revokes_refresh(client: AsyncClient, partner: User):
    """After logout, the old refresh cookie should not issue a new token."""
    await client.post("/auth/login", json=CREDS)
    old_refresh = client.cookies.get(settings.refresh_cookie_name)
    await client.post("/auth/logout")

    # Try using the old refresh token
    client.cookies.set(settings.refresh_cookie_name, old_refresh)
    resp = await client.post("/auth/refresh")
    assert resp.status_code == 401


# ── Firm scoping / visibility ─────────────────────────────────────────────────


async def test_partner_sees_all_mandates(
    db_session: AsyncSession, partner: User, assigned_mandate
):
    ids = await visible_mandate_ids(partner, db_session)
    assert ids is None  # None = no filter applied (sees all)


async def test_analyst_sees_only_assigned_mandates(
    db_session: AsyncSession, analyst: User, assigned_mandate, mandate
):
    ids = await visible_mandate_ids(analyst, db_session)
    assert ids is not None
    assert mandate.id in ids
    assert len(ids) == 1  # only the assigned mandate


async def test_analyst_with_no_assignments_sees_nothing(
    db_session: AsyncSession, analyst: User
):
    ids = await visible_mandate_ids(analyst, db_session)
    assert ids == []


async def test_analyst_firm_scoped_in_me(
    client: AsyncClient, db_session: AsyncSession, analyst: User, firm: Firm
):
    """Analyst /me returns their own firm, not another firm's data."""
    await client.post("/auth/login", json=ANALYST_CREDS)
    resp = await client.get("/auth/me")
    assert resp.status_code == 200
    assert resp.json()["firm"]["id"] == firm.id
    assert resp.json()["role"] == "ANALYST"
