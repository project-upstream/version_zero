# PROGRESS — Project Upstream

Tracks build status, one section per phase. Updated at the end of every phase.

---

## Decisions log
**Plan upgraded to v2 (2026-06-06)** — adopted in full: cookie-based auth, schedule
lifecycle `AWAITING_INITIAL → ACTIVE → STOPPED` with nullable `initial_date`, IST date
math (`today_ist()`), soft-delete (`archived_at`), derived primary contact (no
`primary_contact_id`), `/benchmark`, filter-aware summary envelope, refresh-token
rotation, vertical-slice phasing (Phase 0 now includes the design system + app shell).

Locked choices (incl. two agreed deviations from v2 plan text):
- Auth libs: **python-jose + passlib[bcrypt]** (per v2), `bcrypt` pinned `<4.1` to avoid
  the passlib break.
- DB: async engine, `sqlite+aiosqlite` dev / `postgresql+asyncpg` prod; Alembic via sync driver.
- Cadence: v2 semantics — schedule `AWAITING_INITIAL` until first `INITIAL_EMAIL` (sets
  `initial_date`, activates); fixed-anchor follow-ups; all math in IST.
- Frontend: **Next.js 15** (deviation from v2's "14", per explicit user choice).
- UI: build to plan.md §7.3 tokens (no external design skill available here).
- Seed: no-op without `--reset`.

---

## Phase 0 — Scaffold + design system + shell (v2)  ✅ complete
**Goal:** monorepo skeleton + tooling + frontend design system & app shell; `/health` only.

Backend
- [x] Folder structure (`backend/`, `frontend/`) per plan.md §4
- [x] FastAPI `GET /health`, `pyproject.toml` (§3 deps), `.env.example`, ruff/black
- [x] Async SQLAlchemy engine reading `DATABASE_URL` (`sqlite+aiosqlite` dev)
- [x] `app/core/time.py` with `today_ist()` (Asia/Kolkata)
- [x] CORS with `allow_credentials` + explicit origin; cookie settings in config/.env
- [x] Alembic initialised (sync-migration env via `settings.sync_database_url`)
- [x] `python-jose + passlib[bcrypt]` installed and verified (bcrypt 4.0.1, no passlib break)

Frontend (Next.js 16 + React 19 + Tailwind v4)
- [x] Next.js 16 (App Router, TS) + Tailwind v4 + shadcn/ui (base-nova) + TanStack Query provider + Toaster
- [x] `lib/api.ts` typed client — `credentials: 'include'`, 401 → `/login`; `types/index.ts`
- [x] Design system per §7.3: `StatusBadge` + `CadenceBadge` (exact colour map), `StatCard`,
      `DataTable` wrapper (loading/error/empty states), `EmptyState`, `TableSkeleton`, `PageHeader`
- [x] Left sidebar + top bar shell (role-gated nav via static placeholder `useAuth`) + placeholder
      `/dashboard`; public `/login` placeholder; `/` → `/dashboard` redirect
- [x] `.env.local.example` (`NEXT_PUBLIC_API_URL`); Vitest config + sample test; Playwright config + smoke spec

Root / verify
- [x] `CLAUDE.md`, `README.md`, `PROGRESS.md`, `plan.md`, `docker-compose.yml`, `.gitignore`, `git init` (branch `main`)
- [x] Backend: `pytest` green (1 test); `alembic upgrade head` clean; `/health` → 200
- [x] Frontend: `npm run build` ✅ (typecheck clean, 4 routes); `npm test` ✅ (6 tests);
      `npm run dev` serves `/dashboard` (200, shell renders), `/` 307→/dashboard, `/login` 200 — no console errors

### Environment notes
- **Node 20.18.0** lacks `require(ESM)` (needs 20.19+). Vitest's jsdom deps are ESM-only, so the
  `test` scripts set `NODE_OPTIONS=--experimental-require-module` via `cross-env`. `npm test` just works;
  upgrading to Node ≥ 20.19 makes the flag unnecessary. (`next build`/`dev` are unaffected.)
- `vitest.config.mts` (not `.ts`) so Vitest 4 loads it as ESM.
- Playwright browsers need a one-time `npx playwright install` before `npm run test:e2e`.

### How to run
- Backend: `cd backend && ./.venv/Scripts/python -m uvicorn app.main:app --reload` (docs `/docs`, health `/health`).
  Tests: `./.venv/Scripts/python -m pytest`. Migrate: `./.venv/Scripts/python -m alembic upgrade head`.
- Frontend: `cd frontend && npm run dev` (http://localhost:3000). Tests: `npm test`. Build: `npm run build`.
- Env: copy `backend/.env.example`→`backend/.env` and `frontend/.env.local.example`→`frontend/.env.local`.

---

## Phase 1 — Data model + seed (F-01) ✅ complete

**Goal:** all SQLAlchemy models, Alembic migration, Pydantic schemas, Faker seed.

Backend
- [x] `app/models/enums.py` — all 12 enums (UserRole, MandateType, MandateStatus, CompanyType,
      CompanyStatus, Source, SourceQuality, Engagement, ContactMode, ScheduleStatus,
      OutreachEventType, StoppedReason)
- [x] 8 SQLAlchemy 2.0 model files (one per entity): firm, user, refresh_token, mandate,
      mandate_assignment, company, contact, outreach_schedule, outreach_event
      — all FKs, unique constraints, firm_id on every table, archived_at on
      companies/contacts/mandates, users.token_version, nullable initial_date on schedule,
      AWAITING_INITIAL default; outreach_events has no updated_at (append-only)
- [x] `app/models/__init__.py` imports all models for Alembic autogenerate
- [x] Alembic initial migration generated + applied (`alembic upgrade head` clean)
- [x] Pydantic v2 schemas (Read / Create / Update) for all 8 entities in `app/schemas/`
- [x] `app/seed/seed.py`: 1 firm, 5 users, 4 mandates, 124 companies, 263 contacts, 124
      schedules, 277 events; realistic schedule mix (27 AWAITING / 67 ACTIVE / 30 STOPPED);
      8 deliberate cross-mandate duplicate names; demo logins printed; idempotent without
      `--reset`

**Acceptance criteria verified:**
- `alembic upgrade head` ✅ (all 9 tables created)
- `python -m app.seed.seed --reset` ✅ (clean, re-runnable)
- AWAITING_INITIAL schedules: 27 — none have initial_date set ✅
- All 11 RESPONDED companies have a RESPONSE event ✅
- Every company has exactly 1 primary contact ✅
- 8 cross-mandate duplicate company names across different mandates ✅
- All Pydantic schemas validate from ORM objects ✅
- `pytest` 1/1 ✅ (health check still passes)

**Demo logins** (password for all: `Passw0rd!`):
| Role | Email |
|------|-------|
| PARTNER | partner@upstream.test |
| ANALYST | analyst1@upstream.test |
| ANALYST | analyst2@upstream.test |
| ASSOCIATE | associate1@upstream.test |
| ASSOCIATE | associate2@upstream.test |

**How to run seed:**
```bash
cd backend
python -m app.seed.seed --reset   # wipe + re-seed
python -m app.seed.seed           # add data only (skips if firm exists)
```
## Phase 2 — Auth + roles + firm scoping (F-02/03/04) ✅ complete

**Goal:** cookie-based auth end-to-end + RBAC + first clickable app.

Backend
- [x] `app/core/security.py` — bcrypt hashing, JWT encode/decode, httpOnly cookie helpers,
      refresh-token generation + SHA-256 hashing
- [x] `app/core/deps.py` — `get_current_user` (reads access cookie, checks token_version),
      `require_role(*roles)`, `PartnerOnly`, `visible_mandate_ids(user, db)` (None for partner,
      list[int] for analyst/associate via mandate_assignments)
- [x] `app/api/auth.py` — POST /auth/signup (firm + PARTNER), POST /auth/login,
      POST /auth/refresh (rotation: revoke old, store new hashed), POST /auth/logout
      (revoke + clear cookies), GET /auth/me
- [x] `app/main.py` — auth router mounted
- [x] `tests/conftest.py` — in-memory SQLite (StaticPool) + async client fixtures
- [x] `tests/test_auth.py` — 18 tests: signup, login, wrong creds, /me, cookie required,
      refresh rotation, old-token rejection, token_version bump, logout + revoke,
      partner=None mandates, analyst=assigned only, analyst firm scoped

Frontend
- [x] `/app/login/page.tsx` — React Hook Form + Zod, POST /auth/login, redirect to /dashboard
      on success, field-level validation errors, server error banner
- [x] `/hooks/use-auth.ts` — TanStack Query GET /auth/me, retry:false, 5 min staleTime
- [x] `/app/(app)/layout.tsx` — client-side auth guard: spinner while loading, null (redirect)
      if no session, shell if authenticated
- [x] Topbar + Sidebar null-safe for `user: CurrentUser | null`
- [x] `tests/e2e/login.spec.ts` — Playwright tests: partner/analyst login, wrong password,
      unauthenticated redirect

**Acceptance criteria verified:**
- pytest 19/19 ✅ (18 auth + 1 health)
- Vitest 6/6 ✅ (design system tests unchanged)
- TypeScript typecheck clean ✅
- All auth scenarios: signup, login, wrong creds, refresh rotation, old token rejected,
  token_version bump, logout revokes session ✅
- Analyst firm-scoped: `visible_mandate_ids` returns only assigned mandates ✅
- Partner: `visible_mandate_ids` returns None (= all mandates) ✅
## Phase 3 — Master List API + Companies UI (C-01/02/03/05, X-01) ✅ complete

**Goal:** companies CRUD + cadence-field summary envelope + cross-mandate dupe detection + `/companies` table + `/companies/[id]` detail page.

Backend
- [x] `app/services/cross_mandate.py` — `normalise_name` (strip suffixes/punctuation), `extract_domain` (registrable domain), `find_duplicates` (advisory warning list, X-01)
- [x] `app/api/companies.py` — full router:
  - `_cadence_fields` computes next_due_date / days_remaining / is_overdue server-side (never stored)
  - `_compute_summary` aggregates responded_pct / overdue_count / needs_initial_count / by_status over entire filtered set (not just the page)
  - GET `/companies` with q/status/type/bucket/mandate_id/source/sort/page/page_size/include_archived + summary envelope (C-01/02)
  - POST `/companies` → creates Company + AWAITING_INITIAL schedule + duplicate warnings (C-03/04, X-01)
  - GET `/companies/check-duplicate`
  - GET `/companies/{id}` — full detail with contacts/schedule/events/warnings
  - PATCH `/companies/{id}` — partial update; RESPONDED/BOUNCED/DECLINED status → stops schedule (E-04); `await db.refresh(company)` after commit (server-side `onupdate` fix)
  - DELETE `/companies/{id}` — soft delete (archived_at)
- [x] Firm scoping + analyst visibility enforced on every list/get endpoint
- [x] `tests/test_companies.py` — 15 tests: create+auto-schedule, cross-mandate warning, get/not-found, update, stop-on-respond, soft-delete, list envelope, status filter, name search, summary full-set pagination, analyst visibility, check-duplicate

Frontend
- [x] `types/index.ts` extended — Company, CompanyListResponse, CompanySummary, CompanyDetail, Contact, OutreachEvent, OutreachSchedule, DuplicateWarning, PrimaryContact, Source
- [x] `hooks/use-companies.ts` — useCompanies (with filter QS builder), useCompany, useArchiveCompany, useUpdateCompany
- [x] `app/(app)/companies/page.tsx` — filter-aware stat strip (total / needs-initial / overdue / responded-pct), search + status + type selects + archived toggle, DataTable with Source dot / Type-Bucket / StatusBadge / CadenceBadge / PrimaryContact / HQ columns, pagination
- [x] `app/(app)/companies/[id]/page.tsx` — back + archive actions, header with badges, DuplicateWarning banner, Overview tab (company details + schedule card + notes), Contacts tab, Timeline tab
- [x] `tests/companies-filter.test.tsx` — 5 Vitest unit tests for cadenceStateFromSchedule mapping (AWAITING/STOPPED/overdue/due_soon/upcoming)

**Acceptance criteria verified:**
- pytest 34/34 ✅ (19 auth + 15 companies)
- Vitest 11/11 ✅ (status-badge + companies-filter)
- TypeScript typecheck clean ✅
- GET /companies returns summary envelope with full-set aggregates (not page-only) ✅
- POST /companies creates AWAITING_INITIAL schedule automatically ✅
- PATCH status=RESPONDED stops the schedule ✅
- Soft-delete: archived company excluded from default list, visible with include_archived ✅
- Analyst only sees companies in assigned mandates ✅
- Cross-mandate duplicate warning fires on name/domain match ✅
## Phase 4 — Cadence engine end-to-end (E-01..E-07, C-04 finalize, E-06) ✅ complete

**Goal:** cadence engine fully wired — schedule lifecycle, event logging, work queues, frontend schedule page.

Backend
- [x] `app/services/cadence.py` — `compute_cadence` (fixed-anchor §5.2), `activate_schedule` (AWAITING→ACTIVE, sets immutable initial_date), `stop_schedule`, `pause_schedule` (MANUAL), `resume_schedule`, `EVENT_STOP_MAP` / `EVENT_STATUS_MAP`
- [x] `app/api/companies.py` extended — GET/PATCH `/companies/{id}/schedule`; GET/POST `/companies/{id}/events` (INITIAL_EMAIL activates; RESPONSE/BOUNCE stops + flips status; FOLLOW_UP advances counter; updates contact.last_contact_date)
- [x] `app/api/schedule.py` — GET `/schedule/needs-initial`, `/schedule/due?window=7` (overdue first), `/schedule/overdue`, `/schedule/stats`; all firm+visibility-scoped
- [x] `tests/test_cadence.py` — 14 tests covering cadence math, lifecycle transitions, append-only events, queues, pause/resume

Frontend
- [x] `hooks/use-schedule.ts` — useNeedsInitial, useDue, useOverdue, useScheduleStats, useLogEvent, usePatchSchedule
- [x] `components/features/log-outreach-dialog.tsx` — event-type select + date picker + notes; span.contents trigger wrapper (avoids @base-ui asChild limitation)
- [x] `app/(app)/schedule/page.tsx` — stats strip; grouped sections (Needs first outreach / Overdue / Due today / Due this week) with "Log outreach" per row
- [x] `app/(app)/companies/[id]/page.tsx` — Cadence tab (state, initial date read-only, interval, next due, pause/resume) + Log outreach dialog in tab bar

**Acceptance criteria verified:**
- pytest 48/48 ✅ (34 prior + 14 cadence)
- Vitest 11/11 ✅; TypeScript clean ✅
- compute_cadence matches §5.2 exactly; initial_date immutable once set ✅
- INITIAL_EMAIL activates; RESPONSE stops cadence + flips status; FOLLOW_UP advances counter ✅
- /schedule/due overdue-first; pause→MANUAL; resume→ACTIVE ✅
## Phase 5 — Contacts end-to-end (L-01/02/03) ✅ complete

**Goal:** contacts CRUD (firm-scoped) + primary-contact toggle + touch history + contact list + profile pages.

Backend
- [x] `app/api/contacts.py` — full router:
  - `_get_contact` — firm-scoped, archived-aware lookup
  - `_unset_primary` — enforces ≤1 primary per company (unsets others)
  - GET `/contacts` with q/company_id/engagement/include_archived filters, firm-scoped
  - POST `/contacts` — validates company in firm; is_primary toggle (unsets existing primary); 201
  - GET `/contacts/{id}` — profile + chronological touch history (outreach_events where contact_id=id, asc)
  - PATCH `/contacts/{id}` — partial update; is_primary toggle unsets others; `db.refresh()` after commit
  - DELETE `/contacts/{id}` — soft delete (archived_at = now())
- [x] `app/main.py` — contacts router mounted
- [x] `tests/test_contacts.py` — 14 tests: CRUD, primary toggling (exclusive per company), create-primary unsets existing, primary reflected on company list, touch history assembly (L-03), last_contact_date update on event, soft delete (excluded from default list, visible with include_archived, DB row preserved), firm scoping, auth required

Frontend
- [x] `types/index.ts` extended — ContactDetail (Contact + events[]), ContactListResponse
- [x] `hooks/use-contacts.ts` — useContacts (filters: q/company_id/engagement/include_archived), useContact, useCreateContact, useUpdateContact, useArchiveContact; all mutators invalidate contacts/company/companies queries
- [x] `components/features/contact-dialog.tsx` — create/edit dialog (RHF + Zod); engagement select; is_primary checkbox; span.contents trigger wrapper; coerces empty engagement/email to null
- [x] `app/(app)/contacts/page.tsx` — search input + engagement filter + archived toggle; contact list with Primary badge + last-contact date; links to contact detail
- [x] `app/(app)/contacts/[id]/page.tsx` — profile card (details grid) + touch history timeline; Edit + Archive actions
- [x] `app/(app)/companies/[id]/page.tsx` Contacts tab — "Add contact" button + inline Edit button per contact; uses ContactDialog
- [x] `tests/contact-form.test.tsx` — 8 Vitest unit tests: engagement options correctness, default values, payload coercion (empty engagement/email → null)

**Acceptance criteria verified:**
- pytest 62/62 ✅ (48 prior + 14 contacts)
- Vitest 19/19 ✅ (11 prior + 8 contact-form)
- TypeScript typecheck clean ✅
- POST /contacts creates contact; is_primary=True unsets existing primary for same company ✅
- PATCH /contacts/{id} is_primary toggle unsets others ✅
- GET /contacts/{id} returns chronological outreach_events where contact_id=id (L-03) ✅
- Logging outreach event with contact_id updates contact.last_contact_date ✅
- Soft delete: archived_at set, excluded from default list, visible with include_archived ✅
- All contacts endpoints are firm-scoped; 401 without auth ✅
## Phase 6 — Dashboard + Analytics end-to-end (A-01/A-02 + benchmark + sources) ✅ complete

**Goal:** analytics service + API, mandate benchmark, wired dashboard, analytics page, company benchmark strip.

Backend
- [x] `app/services/analytics.py` — `get_overview` (total, by_status, responded_pct, due_this_week, overdue, needs_initial, active_mandates), `get_response_by_bucket` (A-01, group by bucket), `get_by_analyst` (A-02, by owner_id, events+initial+responses), `get_sources` (group by source×source_quality). "Responded" = `status==RESPONDED` (status stays in sync with events).
- [x] `app/services/benchmark.py` — `get_benchmark`: mandate_response_rate, mandate_avg_touches_to_response, mandate_avg_days_to_response, this_company_touches, this_company_days_to_response (§5.4 exact)
- [x] `app/api/analytics.py` — GET /analytics/overview, /response-by-bucket, /by-analyst (partner only via `require_role`), /sources; all firm+visibility-scoped
- [x] `app/api/companies.py` — appended GET `/companies/{id}/benchmark` (delegates to benchmark service)
- [x] `app/main.py` — analytics router mounted
- [x] `tests/test_analytics.py` — 12 tests: overview coherence, needs-initial count, responded_pct, auth guard, bucket response rate, by-analyst 200 for partner/403 for analyst, event counts, sources structure, benchmark fields, benchmark 404

Frontend
- [x] `hooks/use-analytics.ts` — useAnalyticsOverview, useResponseByBucket, useByAnalyst, useSources, useBenchmark(companyId)
- [x] `app/(app)/dashboard/page.tsx` — KPI strip (total/responded/needs-initial/due-this-week/overdue), status-mix donut (recharts), response-by-bucket bar chart, due-this-week mini-list linked to /schedule; all wired to live API
- [x] `app/(app)/analytics/page.tsx` — response-by-bucket bar chart, source-quality table, by-analyst table (rendered only for PARTNER role)
- [x] `app/(app)/companies/[id]/page.tsx` — BenchmarkStrip component inserted above DuplicateBanner; shows touches/mandate-avg and days-to-response

**Acceptance criteria verified:**
- pytest 74/74 ✅ (62 prior + 12 analytics)
- Vitest 19/19 ✅; TypeScript typecheck clean ✅
- /analytics/overview coherent vs test data; responded_pct > 0 after logging RESPONSE ✅
- /analytics/response-by-bucket groups correctly; response rate > 0 after response event ✅
- /analytics/by-analyst → 200 for partner, 403 for analyst ✅
- /analytics/sources returns rows with source/source_quality/total/response_rate ✅
- /companies/{id}/benchmark returns mandate_response_rate + this_company_touches ✅
- Dashboard renders live KPI cards + charts; analytics page role-gates by-analyst ✅
## Phase 7 — Mandates mgmt + soft-delete UI + polish + deploy ✅ complete

**Goal:** finish mandates end-to-end, soft-delete/unarchive UX everywhere, polish (404/error,
toasts), Playwright critical paths, and deploy docs — closing the §12 Definition of Done.

Backend
- [x] `app/api/mandates.py` — GET `/mandates` (visibility-scoped + per-mandate stats), POST (partner),
      GET `/mandates/{id}` (stats + assignments + lead owner), PATCH (partner), POST `/{id}/archive`
      + `/{id}/unarchive` (partner), GET `/{id}/companies`, POST `/{id}/assignments` + DELETE
      `/{id}/assignments/{user_id}` (partner) — assigning changes the analyst's visible book
- [x] `app/api/users.py` — GET `/users` (firm-scoped) for assignment / lead-owner pickers
- [x] `app/core/deps.py` — added reusable `PartnerDep` annotated dependency
- [x] Unarchive endpoints: POST `/companies/{id}/unarchive`, POST `/contacts/{id}/unarchive` (DoD: restorable)
- [x] `app/main.py` — mandates + users routers mounted
- [x] `tests/test_mandates.py` — 18 tests (scoping, CRUD, role gating, assignment→visibility,
      archive/unarchive, users); + unarchive tests in test_companies/test_contacts

Frontend
- [x] `hooks/use-mandates.ts` + `hooks/use-users.ts`; types: Mandate/MandateListItem/MandateDetail/FirmUser
- [x] `components/features/mandate-dialog.tsx` — create/edit (RHF + Zod, lead-owner picker)
- [x] `app/(app)/mandates/page.tsx` — role-scoped list, stat columns, archived toggle, partner-only create
- [x] `app/(app)/mandates/[id]/page.tsx` — stats, companies mini-list, **assignments management**
      (partner add/remove), edit + archive/unarchive
- [x] `app/(app)/settings/page.tsx` — firm + cadence config + team (closes the nav 404)
- [x] **Create-company dialog** (`components/features/company-dialog.tsx` + `useCreateCompany`) wired into
      `/companies` header — was missing from Phase 3; needed for the create→needs-initial critical path.
      Surfaces cross-mandate duplicate warnings as a toast
- [x] Unarchive (Restore) actions on company + contact detail pages; `/companies?mandate_id=` deep-link filter
- [x] `app/not-found.tsx` (404) + `app/(app)/error.tsx` (error boundary); toasts on create/edit/archive/restore
- [x] Playwright: `tests/e2e/cadence.spec.ts` (create→needs-initial→log initial→due→RESPONSE→stopped),
      `tests/e2e/mandates.spec.ts` (create→archive→restore)
- [x] `tests/mandates.test.tsx` — 3 Vitest unit tests (type/status labels, pct formatting)
- [x] README — full Deploy section (Vercel + Railway/Render, `SameSite=None;Secure` split-origin cookies,
      engine swap via `DATABASE_URL`, daily backups F-04) + Testing section

**Acceptance criteria verified:**
- pytest **94/94** ✅ (74 prior + 18 mandates + 2 unarchive)
- Vitest **22/22** ✅ (19 prior + 3 mandates); TypeScript clean ✅; `npm run build` ✅ (13 routes)
- Mandate list role-scoped; partner assigns an analyst → that mandate enters the analyst's visible book (test) ✅
- Archive/unarchive works across companies/contacts/mandates; archived hidden by default, restorable ✅
- Nav has no dead links (Mandates + Settings now real); 404 + error pages present ✅
- Playwright critical-path specs written (run with both servers + seeded DB) ✅

---

## ✅ BUILD COMPLETE — Definition of Done (§12)

All seven phases (0–7) are done. On a freshly seeded DB:
- Seed → firm + partner/analysts + assignments + ~120 companies + contacts + realistic schedule mix
  + cross-mandate dupes + one primary each; demo logins work.
- Cookie auth; analyst sees only assigned mandates, partner sees all; refresh rotation + logout-everywhere.
- Companies: search/filter/sort/paginate, filter-aware stat strip, archived toggle, create dialog.
- Adding a company auto-creates an AWAITING_INITIAL schedule + warns on cross-mandate dup.
- Work queue (needs-initial + due-this-week, overdue first); initial outreach activates cadence;
  RESPONSE stops it + flips status; cadence numbers match §5.2.
- Company detail: all fields, append-only timeline, contacts (primary flagged), cadence (initial read-only),
  benchmark strip, dup banner.
- Contacts list + profile with chronological touch history; exclusive primary toggle.
- Dashboard + Analytics: scoped stats, response-by-bucket, source quality, partner-only by-analyst.
- Soft delete only; archived hidden by default + restorable everywhere.
- pytest 94 + Vitest 22 green; Playwright critical paths written; frontend builds clean; deploy documented.

### How to demo
1. **Seed:** `cd backend && python -m app.seed.seed --reset` (prints demo logins).
2. **Run:** backend `uvicorn app.main:app --reload`; frontend `npm run dev`.
3. **Log in** as `partner@upstream.test / Passw0rd!` → Dashboard (firm-wide KPIs + charts).
4. **Companies** → search/filter; **New company** → opens its detail (now in *Needs first outreach*).
5. **Log outreach** (Initial email) → cadence activates; **Schedule** shows it under due/overdue queues.
6. Log a **Response** → status flips to Responded, cadence stops (Cadence tab shows stopped reason).
7. **Contacts** → open a profile → chronological touch history; toggle a primary contact.
8. **Mandates** (partner) → open one → assign/unassign an analyst, archive/restore.
9. **Analytics** → response-by-bucket, source quality, by-analyst (partner only).
10. Re-login as `analyst1@upstream.test / Passw0rd!` to see the scoped-down book.
