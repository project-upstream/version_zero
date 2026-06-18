"""Import every model so Alembic autogenerate sees them on Base.metadata."""

from app.models.company import Company as Company
from app.models.contact import Contact as Contact
from app.models.firm import Firm as Firm
from app.models.mandate import Mandate as Mandate
from app.models.mandate_assignment import MandateAssignment as MandateAssignment
from app.models.outreach_event import OutreachEvent as OutreachEvent
from app.models.outreach_schedule import OutreachSchedule as OutreachSchedule
from app.models.refresh_token import RefreshToken as RefreshToken
from app.models.user import User as User

__all__ = [
    "Firm",
    "User",
    "RefreshToken",
    "Mandate",
    "MandateAssignment",
    "Company",
    "Contact",
    "OutreachSchedule",
    "OutreachEvent",
]
