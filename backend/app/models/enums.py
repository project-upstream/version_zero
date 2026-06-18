from __future__ import annotations

import enum


class UserRole(str, enum.Enum):
    ANALYST = "ANALYST"
    ASSOCIATE = "ASSOCIATE"
    PARTNER = "PARTNER"


class MandateType(str, enum.Enum):
    SELL_SIDE = "SELL_SIDE"
    BUY_SIDE = "BUY_SIDE"
    CAPITAL_RAISE = "CAPITAL_RAISE"


class MandateStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ON_HOLD = "ON_HOLD"
    CLOSED = "CLOSED"
    TERMINATED = "TERMINATED"


class CompanyType(str, enum.Enum):
    TARGET = "TARGET"
    BUYER = "BUYER"
    INVESTOR = "INVESTOR"


class CompanyStatus(str, enum.Enum):
    NOT_CONTACTED = "NOT_CONTACTED"
    CONTACTED = "CONTACTED"
    RESPONDED = "RESPONDED"
    INTERESTED = "INTERESTED"
    DECLINED = "DECLINED"
    BOUNCED = "BOUNCED"


class Source(str, enum.Enum):
    PROPRIETARY = "PROPRIETARY"
    PUBLIC = "PUBLIC"
    REFERRAL = "REFERRAL"
    IMPORTED = "IMPORTED"


class SourceQuality(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Engagement(str, enum.Enum):
    BUY_SIDE = "BUY_SIDE"
    SELL_SIDE = "SELL_SIDE"
    INVESTOR = "INVESTOR"
    ADVISOR = "ADVISOR"
    OTHER = "OTHER"


class ContactMode(str, enum.Enum):
    EMAIL = "EMAIL"
    CALL = "CALL"
    LINKEDIN = "LINKEDIN"
    MEETING = "MEETING"
    EVENT = "EVENT"


class ScheduleStatus(str, enum.Enum):
    AWAITING_INITIAL = "AWAITING_INITIAL"
    ACTIVE = "ACTIVE"
    STOPPED = "STOPPED"


class OutreachEventType(str, enum.Enum):
    INITIAL_EMAIL = "INITIAL_EMAIL"
    FOLLOW_UP = "FOLLOW_UP"
    RESPONSE = "RESPONSE"
    BOUNCE = "BOUNCE"
    CALL = "CALL"
    LINKEDIN = "LINKEDIN"
    MEETING = "MEETING"
    NOTE = "NOTE"


class StoppedReason(str, enum.Enum):
    RESPONDED = "RESPONDED"
    BOUNCED = "BOUNCED"
    DECLINED = "DECLINED"
    TERMINATED = "TERMINATED"
    MANUAL = "MANUAL"
