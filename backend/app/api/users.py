"""Users router — read-only firm-user list for assignment dropdowns."""

from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import select

from app.core.deps import CurrentUser, SessionDep
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
async def list_users(db: SessionDep, current_user: CurrentUser):
    """List active users in the caller's firm (id, name, email, role).

    Firm-scoped; names within a firm are not sensitive and are needed for
    mandate-assignment and POC pickers.
    """
    rows = await db.execute(
        select(User)
        .where(User.firm_id == current_user.firm_id, User.is_active.is_(True))
        .order_by(User.full_name)
    )
    return {
        "items": [
            {
                "id": u.id,
                "full_name": u.full_name,
                "email": u.email,
                "role": u.role.value,
            }
            for u in rows.scalars().all()
        ]
    }
