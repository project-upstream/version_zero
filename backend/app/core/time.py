"""Date/time helpers.

All cadence date math is done in IST (Asia/Kolkata) per plan.md §5.2: dates are stored
as DATE (no time); timestamps are UTC.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")


def now_ist() -> datetime:
    """Current timezone-aware datetime in IST."""
    return datetime.now(IST)


def today_ist() -> date:
    """Current calendar date in IST — the anchor for all cadence math."""
    return now_ist().date()


def utcnow() -> datetime:
    """Current timezone-aware UTC datetime (for stored timestamps)."""
    return datetime.now(timezone.utc)
