"""FastAPI reusable dependencies: DB session, current user, RBAC, firm scoping."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import decode_access_token
from app.db.session import get_session
from app.models.enums import UserRole
from app.models.mandate_assignment import MandateAssignment
from app.models.user import User

# ── DB dependency (override this in tests) ────────────────────────────────────

SessionDep = Annotated[AsyncSession, Depends(get_session)]


# ── Auth dependency ───────────────────────────────────────────────────────────


async def get_current_user(
    request: Request,
    db: SessionDep,
) -> User:
    """Read the access cookie, decode the JWT, and return the active user.

    Raises 401 if the cookie is missing, the token is invalid/expired, or the
    user's token_version has been bumped (revoke-all-sessions).
    """
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    raw_token: str | None = request.cookies.get(settings.access_cookie_name)
    if not raw_token:
        raise credentials_exc

    try:
        payload = decode_access_token(raw_token)
        user_id = int(payload["sub"])
        token_version: int = int(payload["ver"])
    except (JWTError, KeyError, ValueError, TypeError):
        raise credentials_exc

    result = await db.execute(
        select(User).where(User.id == user_id, User.is_active.is_(True))
    )
    user = result.scalar_one_or_none()
    if user is None or user.token_version != token_version:
        raise credentials_exc
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


# ── RBAC ─────────────────────────────────────────────────────────────────────


def require_role(*roles: UserRole):
    """Return a dependency that asserts the current user has one of the given roles."""

    async def _check(user: CurrentUser) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return Depends(_check)


PartnerOnly = require_role(UserRole.PARTNER)

# Annotated dependency form for partner-gated routes:
#   async def handler(..., current_user: PartnerDep): ...
PartnerDep = Annotated[User, require_role(UserRole.PARTNER)]


# ── Visibility scoping ────────────────────────────────────────────────────────


async def visible_mandate_ids(user: User, db: AsyncSession) -> list[int] | None:
    """Return the mandate IDs the user may see.

    Partners → None (= all mandates; callers skip the WHERE clause).
    Analysts / Associates → list of mandate IDs via mandate_assignments.
    """
    if user.role == UserRole.PARTNER:
        return None
    result = await db.execute(
        select(MandateAssignment.mandate_id).where(MandateAssignment.user_id == user.id)
    )
    return [row[0] for row in result.all()]
