from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import UserRole
from app.schemas.firm import FirmRead


class UserBase(BaseModel):
    # Plain str, not EmailStr: these schemas echo already-stored data. email-validator
    # rejects RFC-6761 reserved TLDs (.test/.example/.localhost), which would 500 on
    # serialization of the demo `@upstream.test` accounts. Input validation lives on
    # SignupRequest (the one place a new email is actually entered).
    email: str
    full_name: str
    role: UserRole


class UserCreate(UserBase):
    password: str
    firm_id: int


class UserUpdate(BaseModel):
    full_name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    firm_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserWithFirm(UserRead):
    firm: FirmRead
