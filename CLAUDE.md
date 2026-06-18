# Project Upstream — CLAUDE.md

## What this is
A multi-tenant CRM for M&A / investment-banking deal sourcing. It productises three
spreadsheets (Master List, Email Schedule, Contact List) into one connected system.
Greenfield build. Full spec in `plan.md` — read the relevant section before each task.

## Domain glossary
- Firm: the IB firm using the CRM (tenant boundary — everything is firm-scoped).
- Mandate: a deal/engagement (sell-side / buy-side / capital-raise).
- Company (Target/Buyer/Investor): a Master List row, linked to a mandate.
- Contact: a person at a company (firm-scoped, reusable across mandates later).
- Outreach: emails/touches stored as an APPEND-ONLY event log (never columns).
- Cadence: the follow-up schedule, computed from a FIXED anchor = the initial-email date.

## Stack (do not substitute)
- Backend: FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, Alembic, JWT in httpOnly cookies
  (python-jose + passlib[bcrypt]), pytest. DB = SQLite (dev) / PostgreSQL (prod) via DATABASE_URL.
- Frontend: Next.js 16 (App Router) + React 19 + TS, Tailwind v4, shadcn/ui, TanStack Query,
  React Hook Form + Zod, recharts, lucide-react. Vitest + RTL + Playwright for tests. Use the
  frontend-design skill if available; else plan.md §7.3 tokens are authoritative.

## Setup deviations from plan.md (agreed during setup, 2026-06-06)
- **Next.js 16** (+ React 19, Tailwind v4) instead of plan.md §3/§11's "14". `create-next-app@latest`
  now resolves to 16; App Router unchanged, shadcn/ui + TanStack Query compatible (user-approved).
- `bcrypt` pinned `>=4.0.1,<4.1` because passlib 1.7.4 breaks against bcrypt ≥ 4.1.
- Alembic runs migrations through a SYNC driver (`pysqlite`/`psycopg2`) via
  `settings.sync_database_url`; the app engine stays async. One `DATABASE_URL` drives both.
- Async DB driver URLs: `sqlite+aiosqlite:///./upstream.db` dev / `postgresql+asyncpg://` prod.

## Non-negotiable rules
1. Outreach is an append-only event log — never store follow-up dates as columns, never
   mutate/delete an event to "edit history".
2. Cadence (next-due, days-remaining, overdue) is COMPUTED server-side per plan.md §5.2 with
   `today_ist()` (Asia/Kolkata, see `app/core/time.py`); the frontend never recomputes it.
3. A schedule is AWAITING_INITIAL until the first INITIAL_EMAIL is logged (which sets
   initial_date and activates it). initial_date is immutable once set. The clock never ticks
   before the first email is sent.
4. Status RESPONDED/BOUNCED/DECLINED (or a RESPONSE/BOUNCE event) STOPS the cadence.
5. Everything is firm-scoped; analysts see only assigned mandates, partners see all — reuse
   the visibility helper for every list endpoint.
6. SOFT DELETE only (archived_at); the app never hard-deletes. Default queries exclude archived.
7. Primary contact is DERIVED from contacts.is_primary (≤1 per company). No primary_contact_id.
8. Auth = httpOnly Secure cookies (no tokens in JS/localStorage); refresh tokens rotate and are
   revocable. Never return password hashes. Secrets only in .env.

## Conventions
- JSON snake_case; ISO-8601 dates; list responses use the §6.2 summary envelope.
- One SQLAlchemy model per file; Pydantic schemas mirror them.
- Backend: pytest per phase. Frontend: Vitest for components + Playwright for critical paths.
- After each phase, update PROGRESS.md and verify that phase's acceptance checklist.

## Run
- Backend: `cd backend && uvicorn app.main:app --reload` (docs at /docs).
- Seed: `cd backend && python -m app.seed.seed --reset`.
- Frontend: `cd frontend && npm run dev`.
- Demo logins printed by the seed script (analyst + partner).
