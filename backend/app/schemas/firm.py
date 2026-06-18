from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FirmBase(BaseModel):
    name: str


class FirmCreate(FirmBase):
    pass


class FirmRead(FirmBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
