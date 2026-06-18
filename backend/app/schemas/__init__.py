"""Pydantic v2 request/response schemas — one module per entity."""

from app.schemas.company import CompanyCreate as CompanyCreate
from app.schemas.company import CompanyRead as CompanyRead
from app.schemas.company import CompanyUpdate as CompanyUpdate
from app.schemas.contact import ContactCreate as ContactCreate
from app.schemas.contact import ContactRead as ContactRead
from app.schemas.contact import ContactUpdate as ContactUpdate
from app.schemas.firm import FirmCreate as FirmCreate
from app.schemas.firm import FirmRead as FirmRead
from app.schemas.mandate import MandateCreate as MandateCreate
from app.schemas.mandate import MandateRead as MandateRead
from app.schemas.mandate import MandateUpdate as MandateUpdate
from app.schemas.outreach_event import OutreachEventCreate as OutreachEventCreate
from app.schemas.outreach_event import OutreachEventRead as OutreachEventRead
from app.schemas.outreach_schedule import OutreachScheduleRead as OutreachScheduleRead
from app.schemas.outreach_schedule import OutreachScheduleUpdate as OutreachScheduleUpdate
from app.schemas.user import UserCreate as UserCreate
from app.schemas.user import UserRead as UserRead
from app.schemas.user import UserUpdate as UserUpdate
from app.schemas.user import UserWithFirm as UserWithFirm

__all__ = [
    "FirmCreate", "FirmRead",
    "UserCreate", "UserRead", "UserUpdate", "UserWithFirm",
    "MandateCreate", "MandateRead", "MandateUpdate",
    "CompanyCreate", "CompanyRead", "CompanyUpdate",
    "ContactCreate", "ContactRead", "ContactUpdate",
    "OutreachScheduleRead", "OutreachScheduleUpdate",
    "OutreachEventCreate", "OutreachEventRead",
]
