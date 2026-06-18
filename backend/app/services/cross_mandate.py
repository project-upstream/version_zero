"""Cross-mandate duplicate detection — advisory heuristic (X-01).

Normalises company names and domains, then checks whether another company
in the same firm (but a different mandate) looks like the same entity.

Honest limits: exact normalised-name / domain matching will MISS subsidiaries,
holding-company variants ("Tata" vs "Tata Sons"), and DBAs, and may over-match
common words. It is an advisory aid, not entity resolution.
"""

from __future__ import annotations

import re
from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.outreach_schedule import OutreachSchedule

# Suffixes stripped during normalisation
_SUFFIX_RE = re.compile(
    r"\b(pvt|private|ltd|limited|inc|incorporated|llp|llc|co|corp|corporation"
    r"|group|holdings|industries|enterprises|solutions|technologies|tech|india)\b",
    re.IGNORECASE,
)
_PUNCT_RE = re.compile(r"[^\w\s]")
_WS_RE = re.compile(r"\s+")


def normalise_name(name: str) -> str:
    s = name.lower()
    s = _PUNCT_RE.sub(" ", s)
    s = _SUFFIX_RE.sub(" ", s)
    s = _WS_RE.sub(" ", s).strip()
    return s


def extract_domain(url: str | None) -> str | None:
    if not url:
        return None
    try:
        parsed = urlparse(url if "://" in url else f"https://{url}")
        host = parsed.netloc or parsed.path
        # Strip leading www.
        host = re.sub(r"^www\.", "", host).lower()
        # Keep only registrable domain (last two parts)
        parts = host.split(".")
        if len(parts) >= 2:
            return ".".join(parts[-2:])
        return host or None
    except Exception:
        return None


async def find_duplicates(
    db: AsyncSession,
    firm_id: int,
    mandate_id: int,
    company_name: str,
    website: str | None,
) -> list[dict]:
    """Return advisory warnings for companies in the same firm, different mandate,
    that match by normalised name or website domain."""

    norm_name = normalise_name(company_name)
    domain = extract_domain(website)

    # Fetch all non-archived companies in the same firm, different mandate
    result = await db.execute(
        select(Company)
        .where(
            Company.firm_id == firm_id,
            Company.mandate_id != mandate_id,
            Company.archived_at.is_(None),
        )
    )
    candidates = result.scalars().all()

    warnings: list[dict] = []
    seen_ids: set[int] = set()

    for c in candidates:
        if c.id in seen_ids:
            continue
        matched = False
        if norm_name and normalise_name(c.company_name) == norm_name:
            matched = True
        if not matched and domain and extract_domain(c.website) == domain:
            matched = True
        if not matched:
            continue

        # Load the schedule for last_outreach date
        sched_result = await db.execute(
            select(OutreachSchedule).where(OutreachSchedule.company_id == c.id)
        )
        sched = sched_result.scalar_one_or_none()

        seen_ids.add(c.id)
        warnings.append(
            {
                "company_id": c.id,
                "company_name": c.company_name,
                "mandate_id": c.mandate_id,
                "status": c.status,
                "initial_date": sched.initial_date.isoformat() if sched and sched.initial_date else None,
            }
        )

    return warnings
