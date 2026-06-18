from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.enums import CompanyStatus, CompanyType, Source, SourceQuality


class CompanyBase(BaseModel):
    company_name: str
    mandate_id: int
    hq: str | None = None
    type: CompanyType
    status: CompanyStatus = CompanyStatus.NOT_CONTACTED
    rationale: str | None = None
    revenue_source: str | None = None
    revenue_inr_cr: Decimal | None = None
    headcount: int | None = None
    website: str | None = None
    linkedin: str | None = None
    relevant_investments: str | None = None
    bucket: str | None = None
    source: Source = Source.PROPRIETARY
    source_quality: SourceQuality = SourceQuality.MEDIUM


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    company_name: str | None = None
    hq: str | None = None
    type: CompanyType | None = None
    status: CompanyStatus | None = None
    rationale: str | None = None
    revenue_source: str | None = None
    revenue_inr_cr: Decimal | None = None
    headcount: int | None = None
    website: str | None = None
    linkedin: str | None = None
    relevant_investments: str | None = None
    bucket: str | None = None
    source: Source | None = None
    source_quality: SourceQuality | None = None


class CompanyRead(CompanyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    firm_id: int
    created_by_id: int | None
    archived_at: datetime | None
    created_at: datetime
    updated_at: datetime
