"""
Seed script for Project Upstream — India-market demo data.

Usage:
    python -m app.seed.seed           # add data (skip if firm exists)
    python -m app.seed.seed --reset   # drop + recreate + seed

Produces:
  1 firm · 5 users (1 PARTNER, 2 ANALYSTS, 2 ASSOCIATES)
  4 mandates · ~120 companies · 1-3 contacts each · realistic schedule mix
  ~8 deliberate cross-mandate duplicates · demo logins printed
"""

from __future__ import annotations

import argparse
import random
import sys
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from faker import Faker
from passlib.context import CryptContext
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.time import today_ist
from app.db.base import Base
from app.models import (
    Company,
    Contact,
    Firm,
    Mandate,
    MandateAssignment,
    OutreachEvent,
    OutreachSchedule,
    User,
)
from app.models.enums import (
    CompanyStatus,
    CompanyType,
    ContactMode,
    Engagement,
    MandateStatus,
    MandateType,
    OutreachEventType,
    ScheduleStatus,
    Source,
    SourceQuality,
    StoppedReason,
    UserRole,
)

fake = Faker("en_IN")
Faker.seed(42)
random.seed(42)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
DEMO_PASSWORD = "Passw0rd!"

# ── Static data ───────────────────────────────────────────────────────────────

USERS_SPEC = [
    ("Arjun Mehta", "partner@upstream.test", UserRole.PARTNER),
    ("Priya Sharma", "analyst1@upstream.test", UserRole.ANALYST),
    ("Rahul Gupta", "analyst2@upstream.test", UserRole.ANALYST),
    ("Neha Patel", "associate1@upstream.test", UserRole.ASSOCIATE),
    ("Vikram Singh", "associate2@upstream.test", UserRole.ASSOCIATE),
]

MANDATES_SPEC = [
    {
        "client_name": "Medanta Healthcare",
        "name": "Pharma Consolidation — Medanta",
        "type": MandateType.SELL_SIDE,
        "exchange_rate": Decimal("83.12"),
        "exchange_rate_date": date(2024, 3, 1),
        "assigned_indices": [1, 3],  # analyst1, associate1
    },
    {
        "client_name": "IndInfra Capital",
        "name": "PE Infrastructure Buyout — IndInfra",
        "type": MandateType.BUY_SIDE,
        "exchange_rate": Decimal("83.45"),
        "exchange_rate_date": date(2024, 3, 15),
        "assigned_indices": [2, 3],  # analyst2, associate1
    },
    {
        "client_name": "GreenGrow Ventures",
        "name": "AgriTech Capital Raise — GreenGrow",
        "type": MandateType.CAPITAL_RAISE,
        "exchange_rate": Decimal("83.20"),
        "exchange_rate_date": date(2024, 2, 28),
        "assigned_indices": [1, 4],  # analyst1, associate2
    },
    {
        "client_name": "Minda Group",
        "name": "Auto Components M&A — MindaGroup",
        "type": MandateType.SELL_SIDE,
        "exchange_rate": Decimal("83.30"),
        "exchange_rate_date": date(2024, 3, 10),
        "assigned_indices": [2, 4],  # analyst2, associate2
    },
]

# Companies per mandate (29 unique + 1 shared slot = 30)
PHARMA_COMPANIES = [
    ("Sun Pharmaceutical Industries", "Mumbai", "sunpharma.com"),
    ("Dr Reddy's Laboratories", "Hyderabad", "drreddys.com"),
    ("Cipla Ltd", "Mumbai", "cipla.com"),
    ("Lupin Pharmaceuticals", "Mumbai", "lupin.com"),
    ("Aurobindo Pharma", "Hyderabad", "aurobindo.com"),
    ("Alkem Laboratories", "Mumbai", "alkemlabs.com"),
    ("Torrent Pharmaceuticals", "Ahmedabad", "torrentpharma.com"),
    ("Cadila Healthcare", "Ahmedabad", "zyduscadila.com"),
    ("Biocon Ltd", "Bengaluru", "biocon.com"),
    ("Abbott India", "Mumbai", "abbott.com"),
    ("Pfizer India", "Mumbai", "pfizerindia.com"),
    ("Novartis India", "Mumbai", "novartis.com"),
    ("GlaxoSmithKline India", "Mumbai", "gsk.com"),
    ("Sanofi India", "Mumbai", "sanofi.com"),
    ("Jubilant Pharma", "Noida", "jubilantpharma.com"),
    ("Divis Laboratories", "Hyderabad", "divislabs.com"),
    ("Granules India", "Hyderabad", "granulesindia.com"),
    ("Natco Pharma", "Hyderabad", "natcopharma.com"),
    ("Laurus Labs", "Hyderabad", "lauruslabs.com"),
    ("Suven Pharmaceuticals", "Hyderabad", "suven.com"),
    ("Caplin Point Laboratories", "Chennai", "caplinpoint.com"),
    ("Solara Active Pharma", "Mumbai", "solaraactivepharma.com"),
    ("Sequent Scientific", "Mumbai", "sequent.in"),
    ("JB Pharma", "Mumbai", "jbpharma.com"),
    ("Mankind Pharma", "New Delhi", "mankindpharma.com"),
    ("Eris Lifesciences", "Ahmedabad", "eris.co.in"),
    ("Glenmark Pharma", "Mumbai", "glenmarkpharma.com"),
    ("Ipca Laboratories", "Mumbai", "ipca.com"),
    ("Strides Pharma", "Bengaluru", "strides.com"),
]

INFRA_COMPANIES = [
    ("IRB Infrastructure Developers", "Mumbai", "irb.co.in"),
    ("L&T Infrastructure Development", "Mumbai", "larsentoubro.com"),
    ("GMR Airports Infrastructure", "New Delhi", "gmrgroup.in"),
    ("Adani Ports and SEZ", "Ahmedabad", "adaniports.com"),
    ("Container Corporation of India", "New Delhi", "concorindia.com"),
    ("Indus Towers", "Gurugram", "industowers.com"),
    ("Power Grid Corporation", "Gurugram", "powergridindia.com"),
    ("Torrent Power", "Ahmedabad", "torrentpower.com"),
    ("CESC Ltd", "Kolkata", "cesc.co.in"),
    ("Tata Power Company", "Mumbai", "tatapower.com"),
    ("NTPC Ltd", "New Delhi", "ntpc.co.in"),
    ("Greenko Group", "Hyderabad", "greenkogroup.com"),
    ("Hero Future Energies", "New Delhi", "herofutureenergies.com"),
    ("Acme Solar Holdings", "Gurugram", "acmesolar.in"),
    ("Sterlite Power Grid", "Gurugram", "sterlitepower.com"),
    ("Patel Engineering", "Mumbai", "pateleng.com"),
    ("HCC Ltd", "Mumbai", "hcc.com"),
    ("Dilip Buildcon", "Bhopal", "dilipbuildcon.com"),
    ("KNR Constructions", "Hyderabad", "knrconstructions.com"),
    ("PNC Infratech", "Agra", "pncinfratech.com"),
    ("Ashoka Buildcon", "Nashik", "ashokabuildcon.com"),
    ("G R Infraprojects", "Udaipur", "grinfraprojects.com"),
    ("Kalpataru Projects International", "Mumbai", "kalpataruprojects.com"),
    ("Gayatri Projects", "Hyderabad", "gayatriprojects.com"),
    ("ITD Cementation India", "Mumbai", "itdcem.com"),
    ("JMC Projects India", "Ahmedabad", "jmcprojects.com"),
    ("NCC Ltd", "Hyderabad", "nccltd.in"),
    ("MEIL Group", "Hyderabad", "meil.in"),
    ("Shapoorji Pallonji Infra", "Mumbai", "shapoorji.com"),
]

AGRITECH_COMPANIES = [
    ("Mahindra Agri Solutions", "Mumbai", "mahindraagri.com"),
    ("Ninjacart Technologies", "Bengaluru", "ninjacart.in"),
    ("DeHaat AgriTech", "Patna", "agrevolution.in"),
    ("WayCool Foods", "Chennai", "waycoolfoods.com"),
    ("FreshoKartz", "Bengaluru", "freshokartz.com"),
    ("BigHaat Agro", "Bengaluru", "bighaat.com"),
    ("BharatRohan Airborne", "Noida", "bharatrohan.in"),
    ("AgroStar India", "Ahmedabad", "agrostar.in"),
    ("Samunnati Financial", "Chennai", "samunnati.com"),
    ("CropIn Technology", "Bengaluru", "cropin.com"),
    ("Fasal Analytics", "Bengaluru", "fasal.co"),
    ("Intello Labs", "Gurugram", "intellolabs.com"),
    ("Stellapps Technologies", "Bengaluru", "stellapps.com"),
    ("SatSure Analytics", "Bengaluru", "satsure.co"),
    ("Agnext Technologies", "Chandigarh", "agnext.com"),
    ("String Bio", "Bengaluru", "string.bio"),
    ("KissanPro", "Jaipur", "kissanpro.com"),
    ("Gobasco Foods", "Gurugram", "gobasco.com"),
    ("AgriBegri", "Mumbai", "agribegri.com"),
    ("Otipy Fresh", "Gurugram", "otipy.com"),
    ("Bijak AgriFinance", "Gurugram", "bijak.in"),
    ("Kheyti Greenhouses", "Hyderabad", "kheyti.com"),
    ("Jivabhumi Organics", "Bengaluru", "jivabhumi.com"),
    ("FutureFarm Ventures", "Pune", "futurefarm.in"),
    ("Gram Unnati", "Bhopal", "gramunnati.com"),
    ("Fyllo Technologies", "New Delhi", "fyllo.in"),
    ("NFarm Agritech", "Hyderabad", "nfarm.co.in"),
    ("BioD Energy", "Pune", "biodenergy.in"),
    ("Sefai Technologies", "Bengaluru", "sefai.com"),
]

AUTO_COMPANIES = [
    ("Minda Industries", "Gurugram", "mindaind.com"),
    ("Motherson Sumi Systems", "Noida", "motherson.com"),
    ("Bharat Forge", "Pune", "bharatforge.com"),
    ("Endurance Technologies", "Aurangabad", "enduranceindia.com"),
    ("Amara Raja Batteries", "Tirupati", "amararaja.com"),
    ("Exide Industries", "Kolkata", "exideindustries.com"),
    ("JK Tyre & Industries", "New Delhi", "jktyre.com"),
    ("Apollo Tyres", "Gurugram", "apollotyres.com"),
    ("CEAT Ltd", "Mumbai", "ceat.com"),
    ("Balkrishna Industries", "Mumbai", "bkt-tires.com"),
    ("Wabco India", "Chennai", "wabco-india.com"),
    ("Bosch India", "Bengaluru", "boschindia.com"),
    ("Schaeffler India", "Vadodara", "schaeffler.co.in"),
    ("SKF India", "Mumbai", "skfindia.com"),
    ("Timken India", "Kolkata", "timken.com"),
    ("NRB Bearings", "Mumbai", "nrbbearings.com"),
    ("Suprajit Engineering", "Bengaluru", "suprajit.com"),
    ("Gabriel India", "Pune", "gabrielindia.com"),
    ("Lumax Industries", "Gurugram", "lumaxworld.in"),
    ("Sandhar Technologies", "New Delhi", "sandhar.com"),
    ("Minda Corp", "Gurugram", "mindacorp.com"),
    ("Subros Ltd", "Noida", "subros.com"),
    ("Fiem Industries", "New Delhi", "fiemindustries.com"),
    ("Rico Auto Industries", "Gurugram", "ricoauto.in"),
    ("Sharda Motor Industries", "New Delhi", "shardamotor.com"),
    ("Sona BLW Precision", "Gurugram", "sonacoms.com"),
    ("Mahindra CIE Automotive", "Mumbai", "mahindracie.com"),
    ("Ramkrishna Forgings", "Kolkata", "ramkrishnaforgings.com"),
    ("Craftsman Automation", "Coimbatore", "craftsmanautomation.com"),
]

# 8 deliberate cross-mandate duplicate pairs: (company_name, website, mandate_A_idx, mandate_B_idx)
CROSS_MANDATE_DUPES = [
    ("Mahindra Agri Solutions", "mahindraagri.com", 0, 2),   # Pharma + AgriTech
    ("L&T Infrastructure Development", "larsentoubro.com", 1, 3),  # Infra + Auto
    ("Tata Power Company", "tatapower.com", 1, 2),           # Infra + AgriTech
    ("Bosch India", "boschindia.com", 3, 0),                  # Auto + Pharma
    ("Cipla Ltd", "cipla.com", 0, 3),                         # Pharma + Auto
    ("CESC Ltd", "cesc.co.in", 1, 0),                         # Infra + Pharma
    ("Adani Ports and SEZ", "adaniports.com", 1, 3),          # Infra + Auto
    ("Sun Pharmaceutical Industries", "sunpharma.com", 0, 2), # Pharma + AgriTech
]

BUCKETS = ["Strategic", "Financial/PE", "Tier-1", "Tier-2", "Opportunistic"]
HQ_CITIES = [
    "Mumbai", "New Delhi", "Bengaluru", "Hyderabad", "Pune",
    "Chennai", "Kolkata", "Ahmedabad", "Gurugram", "Noida",
]
DESIGNATIONS = [
    "Managing Director", "CEO", "CFO", "COO", "VP Corporate Development",
    "Director M&A", "Head of Strategy", "VP Finance", "General Manager",
    "VP Business Development", "Chief Strategy Officer", "Director Finance",
]


def _days_ago(n: int) -> date:
    return today_ist() - timedelta(days=n)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _hash(password: str) -> str:
    return pwd_context.hash(password)


def _company_lists() -> list[list[tuple[str, str, str]]]:
    return [PHARMA_COMPANIES, INFRA_COMPANIES, AGRITECH_COMPANIES, AUTO_COMPANIES]


def _make_schedule_and_events(
    session: Session,
    company: Company,
    analyst: User,
    target_state: str,  # "awaiting" | "active_ok" | "active_overdue" | "stopped"
) -> None:
    """Create an OutreachSchedule and supporting events for a company."""
    schedule = OutreachSchedule(
        firm_id=company.firm_id,
        company_id=company.id,
        cadence_interval_days=14,
        regarding=f"Introduction re {company.company_name}",
    )

    if target_state == "awaiting":
        schedule.status = ScheduleStatus.AWAITING_INITIAL
        session.add(schedule)
        return

    # ACTIVE variants — initial email was already sent
    if target_state == "active_ok":
        initial_days_ago = random.randint(20, 50)
    elif target_state == "active_overdue":
        initial_days_ago = random.randint(30, 90)
    else:  # stopped
        initial_days_ago = random.randint(40, 120)

    initial_date = _days_ago(initial_days_ago)
    schedule.status = ScheduleStatus.ACTIVE
    schedule.initial_date = initial_date
    session.add(schedule)
    session.flush()  # get schedule.id

    # Log INITIAL_EMAIL event
    session.add(
        OutreachEvent(
            firm_id=company.firm_id,
            company_id=company.id,
            schedule_id=schedule.id,
            event_type=OutreachEventType.INITIAL_EMAIL,
            occurred_on=initial_date,
            regarding=schedule.regarding,
            owner_id=analyst.id,
        )
    )

    # Add some FOLLOW_UP events for companies that have been active a while
    followups = max(0, (initial_days_ago - 14) // 14)
    followups = min(followups, random.randint(1, 4))
    for i in range(1, followups + 1):
        fu_date = initial_date + timedelta(days=i * 14)
        if fu_date <= today_ist():
            session.add(
                OutreachEvent(
                    firm_id=company.firm_id,
                    company_id=company.id,
                    schedule_id=schedule.id,
                    event_type=OutreachEventType.FOLLOW_UP,
                    occurred_on=fu_date,
                    notes=f"Follow-up #{i}",
                    owner_id=analyst.id,
                )
            )

    if target_state == "stopped":
        stop_reason_choices = [
            (StoppedReason.RESPONDED, CompanyStatus.RESPONDED),
            (StoppedReason.DECLINED, CompanyStatus.DECLINED),
            (StoppedReason.BOUNCED, CompanyStatus.BOUNCED),
        ]
        stopped_reason, new_status = random.choice(stop_reason_choices)

        schedule.status = ScheduleStatus.STOPPED
        schedule.stopped_reason = stopped_reason
        schedule.stopped_at = _utcnow()
        company.status = new_status

        if stopped_reason == StoppedReason.RESPONDED:
            session.add(
                OutreachEvent(
                    firm_id=company.firm_id,
                    company_id=company.id,
                    schedule_id=schedule.id,
                    event_type=OutreachEventType.RESPONSE,
                    occurred_on=_days_ago(random.randint(5, 30)),
                    notes="Positive response received.",
                    owner_id=analyst.id,
                )
            )
        elif stopped_reason == StoppedReason.BOUNCED:
            session.add(
                OutreachEvent(
                    firm_id=company.firm_id,
                    company_id=company.id,
                    schedule_id=schedule.id,
                    event_type=OutreachEventType.BOUNCE,
                    occurred_on=_days_ago(random.randint(5, 20)),
                    notes="Email bounced — address invalid.",
                    owner_id=analyst.id,
                )
            )
    elif target_state in ("active_ok", "active_overdue"):
        if target_state == "active_ok":
            company.status = CompanyStatus.CONTACTED
        else:
            company.status = CompanyStatus.CONTACTED
            if random.random() < 0.3:
                company.status = CompanyStatus.INTERESTED


def _make_contacts(
    session: Session,
    company: Company,
    analyst: User,
    n: int,
) -> None:
    """Create n contacts for a company; exactly one is_primary."""
    primary_idx = random.randint(0, n - 1)
    for i in range(n):
        name = fake.name()
        is_primary = i == primary_idx
        session.add(
            Contact(
                firm_id=company.firm_id,
                company_id=company.id,
                contact_person=name,
                designation=random.choice(DESIGNATIONS),
                email=f"{name.lower().replace(' ', '.')}.{fake.random_int(10, 99)}@{company.website or 'example.com'}",
                phone=fake.phone_number()[:20],
                engagement=random.choice(list(Engagement)),
                date_connected=_days_ago(random.randint(10, 200)),
                mode=random.choice(list(ContactMode)),
                poc_owner_id=analyst.id,
                is_primary=is_primary,
                remark=fake.sentence(nb_words=6) if random.random() > 0.5 else None,
            )
        )


def _make_company(
    session: Session,
    firm: Firm,
    mandate: Mandate,
    analyst: User,
    name: str,
    hq: str,
    website: str,
    target_state: str,
) -> Company:
    source = random.choice(list(Source))
    company = Company(
        firm_id=firm.id,
        mandate_id=mandate.id,
        company_name=name,
        hq=hq,
        type=random.choice([CompanyType.TARGET, CompanyType.BUYER, CompanyType.INVESTOR]),
        status=CompanyStatus.NOT_CONTACTED,
        rationale=fake.sentence(nb_words=10),
        revenue_source="Annual report / public filing",
        revenue_inr_cr=Decimal(str(round(random.uniform(50, 15000), 2))),
        headcount=random.randint(50, 50000),
        website=f"https://www.{website}",
        bucket=random.choice(BUCKETS),
        source=source,
        source_quality=random.choice(list(SourceQuality)),
        created_by_id=analyst.id,
    )
    session.add(company)
    session.flush()
    _make_contacts(session, company, analyst, random.randint(1, 3))
    _make_schedule_and_events(session, company, analyst, target_state)
    return company


def _pick_state(i: int, total: int) -> str:
    """Assign a schedule state based on position in a mandate's company list."""
    pct = i / total
    if pct < 0.20:
        return "awaiting"
    elif pct < 0.50:
        return "active_ok"
    elif pct < 0.75:
        return "active_overdue"
    else:
        return "stopped"


def run_seed(session: Session) -> None:
    # ── Firm ──────────────────────────────────────────────────────────────────
    firm = Firm(name="Upstream Capital Advisors")
    session.add(firm)
    session.flush()

    # ── Users ─────────────────────────────────────────────────────────────────
    users: list[User] = []
    for full_name, email, role in USERS_SPEC:
        u = User(
            firm_id=firm.id,
            email=email,
            hashed_password=_hash(DEMO_PASSWORD),
            full_name=full_name,
            role=role,
        )
        session.add(u)
        users.append(u)
    session.flush()

    partner = users[0]

    # ── Mandates + assignments ────────────────────────────────────────────────
    mandates: list[Mandate] = []
    for spec in MANDATES_SPEC:
        m = Mandate(
            firm_id=firm.id,
            client_name=spec["client_name"],
            name=spec["name"],
            type=spec["type"],
            status=MandateStatus.ACTIVE,
            exchange_rate=spec["exchange_rate"],
            exchange_rate_date=spec["exchange_rate_date"],
            lead_owner_id=partner.id,
        )
        session.add(m)
        mandates.append(m)
    session.flush()

    for spec, mandate in zip(MANDATES_SPEC, mandates):
        for idx in spec["assigned_indices"]:
            session.add(
                MandateAssignment(mandate_id=mandate.id, user_id=users[idx].id)
            )
    session.flush()

    # ── Helper: pick analyst for a mandate ───────────────────────────────────
    def analyst_for(mandate_idx: int) -> User:
        assigned = MANDATES_SPEC[mandate_idx]["assigned_indices"]
        # First assigned user is the analyst/associate
        return users[assigned[0]]

    # ── Companies per mandate ────────────────────────────────────────────────
    all_lists = _company_lists()
    dupe_added: set[tuple[int, str]] = set()  # (mandate_idx, name)

    for m_idx, (mandate, co_list) in enumerate(zip(mandates, all_lists)):
        analyst = analyst_for(m_idx)
        random.shuffle(co_list)
        for i, (name, hq, website) in enumerate(co_list):
            state = _pick_state(i, len(co_list))
            _make_company(session, firm, mandate, analyst, name, hq, website, state)
            dupe_added.add((m_idx, name))

    # ── Cross-mandate duplicates ──────────────────────────────────────────────
    for name, website, m_idx_a, m_idx_b in CROSS_MANDATE_DUPES:
        # Add the duplicate into mandate B (the company already exists in mandate A from above)
        target_mandate_idx = m_idx_b if (m_idx_a, name) in dupe_added else m_idx_a
        mandate = mandates[target_mandate_idx]
        analyst = analyst_for(target_mandate_idx)
        # Pick HQ from original list or fallback
        hq = random.choice(HQ_CITIES)
        state = random.choice(["awaiting", "active_ok", "stopped"])
        _make_company(session, firm, mandate, analyst, name, website, website, state)

    session.commit()

    # ── Print summary ─────────────────────────────────────────────────────────
    import sqlalchemy as sa

    def _count(model: type) -> int:
        return session.execute(sa.select(sa.func.count()).select_from(model)).scalar() or 0

    company_count = _count(Company)
    contact_count = _count(Contact)
    schedule_count = _count(OutreachSchedule)
    event_count = _count(OutreachEvent)

    sep = "-" * 65
    print(f"\n{sep}")
    print("  Seed complete")
    print(sep)
    print(f"  Firm:       {firm.name}")
    print(f"  Users:      {len(users)} (1 partner, 2 analysts, 2 associates)")
    print(f"  Mandates:   {len(mandates)}")
    print(f"  Companies:  {company_count} (incl. ~8 cross-mandate dupes)")
    print(f"  Contacts:   {contact_count}")
    print(f"  Schedules:  {schedule_count}")
    print(f"  Events:     {event_count}")
    print(sep)
    print("Demo logins (password for all: Passw0rd!):")
    for u in users:
        print(f"  {u.role.value:<10}  {u.email}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the Upstream CRM database.")
    parser.add_argument("--reset", action="store_true", help="Wipe all data before seeding.")
    args = parser.parse_args()

    import sqlalchemy as sa

    engine = create_engine(settings.sync_database_url, echo=False)
    Base.metadata.create_all(engine)  # ensure tables exist (idempotent)

    # Check for existing data in its own session so it doesn't pollute the seed session.
    with Session(engine) as check_session:
        existing = check_session.execute(sa.select(Firm)).first()

    if existing and not args.reset:
        print("Database already seeded. Use --reset to wipe and re-seed.")
        sys.exit(0)

    if args.reset:
        print("Resetting database...")
        with Session(engine) as reset_session:
            for table in reversed(Base.metadata.sorted_tables):
                reset_session.execute(table.delete())
            reset_session.commit()

    print("Seeding...")
    with Session(engine) as seed_session:
        run_seed(seed_session)


if __name__ == "__main__":
    main()
