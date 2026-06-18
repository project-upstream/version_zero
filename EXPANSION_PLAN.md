# Project Upstream — Expansion Build Plan

### Projects-First Workspace · Sourcing Layer · AI · Email & Scheduling · Data Ingest

**Phases 8–16 (post-MVP)** · Companion to [`plan.md`](plan.md) (MVP v2 spec) and [`PROGRESS.md`](PROGRESS.md) (build log) · Last updated 2026-06-11

> **Read order for the implementer:** [`CLAUDE.md`](CLAUDE.md) → the relevant `plan.md` section → this document's section for the phase you're on → [`UI_ENHANCEMENT_PLAN.md`](UI_ENHANCEMENT_PLAN.md) for visual tokens. This file is the authoritative spec for everything *after* the MVP Definition of Done.

---

## 0. How to use this document

The MVP (Phases 0–7) is **complete and green** — Master List, cadence engine, Contact List, cross-mandate dedupe, analytics, mandates, cookie auth, soft-delete. 94 backend tests + 22 frontend tests pass. This document specifies the next chapter, mapped to the PRD's deferred features:

- **Feature 2 — Sourcing Layer** (S-01 … S-07)
- **Feature 3 — Suggested additions** (P-01 … P-06)
- The **Projects-first workspace** reorganisation shown in the new mockups
- The **AI layer** that accelerates all of the above
- The **email/scheduling + data-ingest** plumbing that feeds the platform real data

**Working method (unchanged from MVP):**
1. Build **one phase at a time** (§14). Each phase is a vertical slice that ships something clickable.
2. Every phase ends with its acceptance checklist green (pytest + Vitest/Playwright) and a `PROGRESS.md` entry.
3. The data model is the moat — land the schema additions (§5) before the UI for each slice.
4. **Everything stays firm-scoped and visibility-scoped.** Reuse `visible_mandate_ids(user, db)` and the firm filter on *every* new endpoint, exactly as the MVP does. No exceptions.

**The two hard constraints the user set:**
- **Build key-optional.** No third-party API key (LLM, email, enrichment) is available yet. Every integration ships with a **deterministic mock provider** so the full feature works end-to-end on seed data today, and swaps to the real provider by setting one env var when the key arrives (§6.2, §6.4).
- **Real data drives the platform.** Two ingest rails feed it: **(a) Excel/CSV upload** (§9) and **(b) the user's connected mailbox** (§8). Both normalise into the same schema and auto-populate the workspace.

---

## 1. Where we are vs. where we're going (gap analysis)

| Capability | MVP today | This plan adds |
|---|---|---|
| Deal container | `Mandate` (partner-created) | **"Project"** = the user-facing mandate; analysts can create them; pin, project switcher (§10) |
| Personas / views | One UI for everyone | **Role-aware:** analyst = operator (project cockpit), partner = overseer (firm portfolio) — same data, different defaults (§10.0) |
| Buy/sell distinction | `MandateType` field only | **Type-aware workspace** — buy-side/sell-side/cap-raise relabel the noun, add-button, columns, sourcing presets (§10.1) |
| In-project work surface | Plain companies table | **Split-pane worklist cockpit** (Worklist/Board/Table + preview pane, bulk, keyboard) (§10.5) |
| Dashboard | One firm-wide dashboard | **Per-project dashboard** + **exec firm-portfolio** (per-analyst + dupe alerts) (§10.6/10.7) |
| Company list | Per-mandate Master List | + a firm-level **Companies directory** and a **Sourcing pool** that feeds mandates (§7) |
| Getting data in | Manual create dialog + Faker seed | **Excel/CSV import wizard** + **mailbox auto-log** (§8, §9) |
| Outreach logging | Manual "Log outreach" dialog | + **Send-from-platform** (auto-logs) and **inbox sync auto-log** of touches sent from the user's own client (§8) |
| Finding targets | None | **Sourcing search** over the pool by mandate thesis, one-click push to Master List (§7) |
| Intelligence | Computed cadence + analytics | **AI** signals-based ranking, thesis-match + monitor, enrichment, email drafting, company brief — all key-optional (§6, §19.4) |
| Relationship intel | Cross-mandate memory stored, not surfaced | **Warm-path panel + relationship-strength score** (§10.5, X-02) — the market's #1 analyst ask after auto-capture (§19.2) |
| Stalled-deal detection | None | **"Going cold" signal** from email silence, for analyst + partner (§10.5/10.6, A-03, §19.3) |
| Auth | Email + password (cookies) | + **Google / Microsoft OAuth** sign-in and mailbox connection (§8.1) |
| Reminders | In-app queues | **Daily digest** email + in-app notifications (P-03, §8.6) |
| Reporting out | In-app only | **Export to Excel/PDF** (P-05, §11.3) |
| Templates / audit | None | **Email templates** (P-02) + **per-project activity timeline** (P-04, §11) |

**Design rule that governs the whole expansion:** the MVP's append-only outreach log, fixed-anchor cadence, soft-delete, and firm-first scoping are *invariants*. New features feed those primitives; they never bypass them. A platform-sent email and a mailbox-synced email both land as ordinary `OutreachEvent` rows and drive the same cadence engine.

---

## 2. Scope of this expansion

### In scope
- **S-01** Proprietary DB ingest (analyst's existing company/contact DB → sourcing schema, deduped/normalised)
- **S-02** Public-source companies via CSV import into the pool
- **S-03** Search the sourcing pool by mandate criteria (sector/geo/size/type)
- **S-04** One-click push of candidates into a project's Master List (starts cadence)
- **S-05** Enrichment fields on candidate cards
- **S-06** Pluggable external data sources (architecture only — no paid feed wired)
- **S-07** AI-assisted ranking/suggestions (mock-first)
- **P-01** Outlook/Gmail send + auto-log; inbox-sync auto-log of externally-sent touches
- **P-02** Reusable email templates with merge fields
- **P-03** Email + in-app reminders / daily digest
- **P-04** Per-mandate (per-project) activity timeline
- **P-05** Export mandate list / status to Excel/PDF
- **P-06** Spreadsheet-import onboarding wizard
- **Projects-first UX**: project index with cards (pinned, status, side tag), project switcher, per-project dashboard, analyst-created projects

### Explicitly out of scope (still deferred)
- Building a proprietary company-data business (firmographics moat) — we *integrate*, never *rebuild* (PRD §7.2). §7's external-source layer is an interface, not a data acquisition project.
- Mass email / marketing automation (we send analyst-paced 1:1 touches, not blasts).
- Midstream deal execution (NDA, bid management, diligence), valuation/IM/CIM tooling.
- Real-time bidirectional CRM sync with Salesforce/DealCloud.
- A full permissions matrix beyond the existing ANALYST / ASSOCIATE / PARTNER roles (we extend who-can-create-projects; we do not introduce custom roles).

---

## 3. Guiding principles (extends `CLAUDE.md`)

These are additive non-negotiables for this chapter. Keep `CLAUDE.md`'s eight rules in force; add:

9. **Key-optional by construction.** Every external dependency (LLM, email transport, enrichment) sits behind a small interface with a `mock` implementation selected by config. The product is fully demonstrable with zero secrets. Real keys are a config flip, never a code change. (§6.4, §17)
10. **Provenance is permanent.** Every company/contact/event records where it came from (`source`, `import_batch_id`, `email_message_id`, `ai_suggestion_id`). Imports and syncs are auditable and reversible (soft-delete + batch rollback). Never silently overwrite analyst-entered fields during enrichment — enrichment is *suggested*, applied on accept (§5.3, §7.5).
11. **The sourcing pool is firm-level, not mandate-level.** A `SourcingCandidate` is reusable across projects — that is the cross-mandate moat. Pushing a candidate into a project *materialises* a `Company` row linked back to the candidate; it never moves the candidate. (§7.1)
12. **AI is an accelerant, never an authority.** AI output is always a *suggestion* surfaced for human accept/edit/reject, always attributed, never auto-committed to the system of record. Cadence, dedupe-final, status changes stay deterministic/server-side. (§6.5)
13. **OAuth tokens are secrets at rest.** Mailbox refresh tokens are encrypted column-level (Fernet/KMS), never returned to the client, firm-scoped, revocable. The mailbox connection is per-user; the data it produces is firm-scoped. (§5.4, §16)
14. **One ingest normaliser.** CSV import, mailbox sync, and (later) external feeds all converge on the same normalise + dedupe service that the MVP's `cross_mandate.py` already started. No parallel dedupe logic. (§7.2)
15. **Auto-capture over manual entry.** Research is unanimous: manual data-entry burden is the #1 reason dealmakers abandon CRMs (§19.1). Email **auto-capture is the keystone adoption feature**, not a "suggested" extra — the manual "Log outreach" dialog is the *fallback*. Every feature should reduce keystrokes for the analyst, never add them. (§8, §19)
16. **Self-serve, zero-admin.** Our wedge vs DealCloud (months of config, dedicated admins) is Affinity-grade simplicity: a firm is live in minutes via the import wizard, no consultant, no trained admin to change a field or dashboard. Prefer sensible defaults + inline config over settings screens. (§19.5)

---

## 4. Architecture additions

```
backend/app/
  integrations/                # NEW — all external-world adapters live here
    __init__.py
    base.py                    # Provider protocols (LLMProvider, MailProvider, EnrichmentProvider, OAuthProvider)
    registry.py                # config-driven provider selection (mock | real)
    llm/
      mock.py                  # deterministic, key-free
      anthropic.py             # Claude via Anthropic SDK (claude-opus-4-8 / haiku for cheap jobs)
      openai.py                # optional alt
    mail/
      mock.py                  # logs "sent" to DB, no network
      gmail.py                 # Gmail API (send + history sync)
      graph.py                 # Microsoft Graph (Outlook)
    enrichment/
      mock.py                  # synthesises firmographics deterministically from name/domain
      clearbit_like.py         # interface stub for a future paid feed (S-06)
    oauth/
      google.py
      microsoft.py
  services/
    sourcing.py                # NEW — search pool, scoring, push-to-mandate (S-03/04)
    ingest.py                  # NEW — CSV/Excel parse → normalise → dedupe → stage (S-01/02, P-06)
    dedupe.py                  # NEW — promotes cross_mandate.py heuristics to a shared normaliser (§7.2)
    ai.py                      # NEW — orchestrates LLM jobs (rank/match/enrich/draft), caching + audit
    email.py                   # NEW — compose, schedule, send (→ auto-log), inbox sync auto-log (P-01)
    templates.py               # NEW — render templates with merge fields (P-02)
    digest.py                  # NEW — build + send daily reminder digest (P-03)
    export.py                  # NEW — Excel (openpyxl) + PDF (weasyprint/reportlab) (P-05)
    activity.py                # NEW — per-project activity feed assembly (P-04)
    crypto.py                  # NEW — Fernet encrypt/decrypt for OAuth token columns (§16)
  workers/                     # NEW — background jobs (see §4.1)
    __init__.py
    queue.py                   # abstraction (in-process now; Celery/RQ/Arq later)
    tasks.py                   # send_scheduled_email, sync_mailbox, run_ai_job, send_digests
  api/
    sourcing.py  ingest.py  email.py  integrations.py  ai.py  templates.py
    notifications.py  export.py  activity.py  projects.py   # NEW routers
```

```
frontend/app/(app)/
  projects/                    # NEW — project index (the mockup) + switcher source of truth
    page.tsx
    [id]/page.tsx              # per-project dashboard (the second mockup)
    [id]/sourcing/page.tsx     # sourcing pool scoped to this project's thesis
    [id]/companies/page.tsx    # project Master List (today's /companies, project-scoped)
    [id]/timeline/page.tsx     # per-project activity feed (P-04)
  sourcing/page.tsx            # firm-level pool + search (S-03)
  import/page.tsx              # CSV/Excel import wizard (P-06)
  settings/integrations/page.tsx  # connect Gmail/Outlook, AI key status, source feeds
  templates/page.tsx           # email templates (P-02)
components/features/
  project-card.tsx  project-switcher.tsx  candidate-card.tsx  import-wizard/*
  worklist-cockpit.tsx  preview-pane.tsx  lens-switcher.tsx  board-view.tsx   # analyst cockpit (§10.5)
  exec-portfolio.tsx                                                          # partner roll-up (§10.6)
  email-composer.tsx  template-picker.tsx  ai-suggestion-panel.tsx  enrichment-diff.tsx
hooks/
  use-mandate-vocab.ts   # buy/sell/cap-raise relabeling (§10.1)
  use-role-home.ts       # role-aware default landing (§10.0)
```

### 4.1 Background work

Several features are inherently asynchronous: scheduled email send, mailbox polling, AI batch ranking, daily digests, large CSV imports. Introduce a **thin queue abstraction** (`workers/queue.py`) with two backends:

- **Dev / now:** FastAPI `BackgroundTasks` + an in-process async scheduler (APScheduler) — zero infra, works on SQLite. Good enough to demo every feature.
- **Prod / later:** swap the backend to **Arq** (async-native, Redis) or Celery. The task functions in `workers/tasks.py` don't change; only `queue.py`'s `enqueue()` / scheduler binding changes.

A `scheduled_email` / `ai_job` / `sync_cursor` row is the source of truth; the worker is stateless and idempotent (claim-by-status, dedupe by external id). This keeps "scheduled send" and "auto-log" correct even if a worker restarts.

---

## 5. Data model additions

> All new tables carry `firm_id` (indexed) and follow MVP conventions: one model per file, Pydantic v2 schemas mirror them, `created_at`/`updated_at`, soft-delete (`archived_at`) where user-facing, and an Alembic migration per phase. Money stays `Numeric`; dates ISO-8601; enums `native_enum=False` (matches existing models).

### 5.0 New enums (`models/enums.py`)

```python
class ProjectStage(str, enum.Enum):      # user-facing project status (mockup: IN PROGRESS / ABANDONED)
    IN_PROGRESS = "IN_PROGRESS"
    ON_HOLD     = "ON_HOLD"
    WON         = "WON"
    ABANDONED   = "ABANDONED"

class CandidateStatus(str, enum.Enum):   # sourcing pool lifecycle
    POOL       = "POOL"          # in the pool, not yet on a mandate
    SHORTLISTED= "SHORTLISTED"
    PUSHED     = "PUSHED"        # materialised as a Company on ≥1 mandate
    REJECTED   = "REJECTED"      # analyst dismissed for this thesis

class ImportStatus(str, enum.Enum):
    UPLOADED = "UPLOADED"; MAPPING = "MAPPING"; VALIDATING = "VALIDATING"
    READY = "READY"; COMMITTED = "COMMITTED"; FAILED = "FAILED"; ROLLED_BACK = "ROLLED_BACK"

class EmailProvider(str, enum.Enum):   GOOGLE = "GOOGLE"; MICROSOFT = "MICROSOFT"; MOCK = "MOCK"

class EmailDirection(str, enum.Enum):  OUTBOUND = "OUTBOUND"; INBOUND = "INBOUND"

class EmailStatus(str, enum.Enum):
    DRAFT = "DRAFT"; SCHEDULED = "SCHEDULED"; SENDING = "SENDING"; SENT = "SENT"
    FAILED = "FAILED"; RECEIVED = "RECEIVED"   # RECEIVED = inbound, synced

class AIJobType(str, enum.Enum):
    RANK_CANDIDATES = "RANK_CANDIDATES"; THESIS_MATCH = "THESIS_MATCH"
    ENRICH = "ENRICH"; DRAFT_EMAIL = "DRAFT_EMAIL"; DEDUPE_ASSIST = "DEDUPE_ASSIST"
    COMPANY_SUMMARY = "COMPANY_SUMMARY"      # one-paragraph brief from fields+timeline+notes (§19.4)
    RELATIONSHIP_INTEL = "RELATIONSHIP_INTEL"  # warm-path / relationship-strength assist (§19.4-#2)

class AIJobStatus(str, enum.Enum):  PENDING="PENDING"; RUNNING="RUNNING"; DONE="DONE"; FAILED="FAILED"

class SuggestionState(str, enum.Enum):  PROPOSED="PROPOSED"; ACCEPTED="ACCEPTED"; REJECTED="REJECTED"; EDITED="EDITED"

class NotificationType(str, enum.Enum):
    DUE_SOON="DUE_SOON"; OVERDUE="OVERDUE"; RESPONSE="RESPONSE"
    IMPORT_DONE="IMPORT_DONE"; AI_DONE="AI_DONE"; DIGEST="DIGEST"
```

### 5.1 Project layer — extend `Mandate`, don't replace it

**Decision (recommended):** "Project" is the **user-facing name for a Mandate**. The backend keeps the `mandates` table and all its relationships (companies, schedules, assignments, cross-mandate moat) — renaming the table would be a high-risk migration for zero domain benefit, and `CLAUDE.md`'s glossary already equates the two ("Mandate: a deal/engagement"). The UI says "Project"; the API can expose `/projects` as an alias router over the same service, or simply relabel `/mandates` in the client. Add these columns to `Mandate`:

```python
# mandate.py — additive columns
stage:        Mapped[ProjectStage]   = mapped_column(SAEnum(ProjectStage, native_enum=False),
                                                      default=ProjectStage.IN_PROGRESS, nullable=False)
pinned_by_id: Mapped[int | None]     = mapped_column(ForeignKey("users.id"), nullable=True)  # per-user pin → see UserProjectPref
thesis:       Mapped[str | None]     = mapped_column(Text, nullable=True)   # sector/geo/size/rationale free-text → feeds sourcing + AI
sector:       Mapped[str | None]     = mapped_column(String(120), nullable=True)
geography:    Mapped[str | None]     = mapped_column(String(120), nullable=True)
size_band:    Mapped[str | None]     = mapped_column(String(60), nullable=True)
```

> `stage` (IN_PROGRESS/ON_HOLD/WON/ABANDONED) is the **mockup's project badge** and is distinct from the engine-level `MandateStatus` (ACTIVE/ON_HOLD/CLOSED/TERMINATED) which still drives cadence stop-on-TERMINATED. Map them: setting `stage=ABANDONED` or `WON` sets `MandateStatus=TERMINATED`/`CLOSED` under the hood so cadence stops correctly. Surface only `stage` in the UI.

**Per-user pinning & "current project"** — pinning and the selected project are per-user, so they go in their own table:

```python
class UserProjectPref(Base):          # user_project_prefs
    id, firm_id, user_id (FK), mandate_id (FK)
    pinned: bool = False
    last_opened_at: datetime | None
    __table_args__ = (UniqueConstraint("user_id", "mandate_id"),)
```

**Permission change (user requirement):** analysts may **create** projects. Update the mandates router: `POST /mandates` allowed for ANALYST/ASSOCIATE/PARTNER (was PARTNER-only). On analyst create, auto-assign the creator (`MandateAssignment`) and set `lead_owner_id = creator` so it enters their visible book immediately. Partner-only actions (archive, reassign other people, firm-wide settings) stay gated.

### 5.2 Sourcing pool

```python
class SourcingCandidate(Base):        # sourcing_candidates  — FIRM-LEVEL, reusable across mandates
    id, firm_id (idx)
    company_name: str                 # normalised display name
    normalised_name: str (idx)        # from dedupe.normalise_name — for matching
    domain: str | None (idx)          # registrable domain — primary dedupe key
    hq, sector, geography: str | None
    revenue_inr_cr: Numeric | None
    headcount: int | None
    website, linkedin: str | None
    description: Text | None
    type: CompanyType                 # TARGET/BUYER/INVESTOR (intended use)
    source: Source                    # PROPRIETARY/PUBLIC/REFERRAL/IMPORTED
    source_quality: SourceQuality
    status: CandidateStatus = POOL
    enrichment: JSON | None           # raw provider payload (provenance), applied fields copied to columns
    import_batch_id: FK | None        # provenance (5.3)
    created_by_id: FK | None
    archived_at, created_at, updated_at
    # relationships: contacts (CandidateContact), pushes (CandidatePush)

class CandidateContact(Base):         # candidate_contacts — person rows attached to a pool candidate
    id, firm_id, candidate_id (FK)
    full_name, designation, email, phone, linkedin: str | None
    is_primary: bool = False

class CandidatePush(Base):            # candidate_pushes — provenance of pool → Master List
    id, firm_id, candidate_id (FK), mandate_id (FK), company_id (FK)   # the materialised Company
    pushed_by_id (FK), created_at
    __table_args__ = (UniqueConstraint("candidate_id", "mandate_id"),)  # one push per (candidate, mandate)
```

`Company` gains one nullable provenance column: `source_candidate_id: FK | None` (links a materialised company back to its pool candidate, enabling "already on Project X" badges and cross-mandate reuse counts).

### 5.3 Import pipeline

```python
class ImportBatch(Base):              # import_batches
    id, firm_id, uploaded_by_id (FK)
    filename: str; kind: str          # "candidates" | "companies" | "contacts"
    target_mandate_id: FK | None      # if importing straight into a project's Master List
    status: ImportStatus
    column_map: JSON | None           # {source_header: canonical_field}
    row_count, inserted_count, updated_count, skipped_count, error_count: int
    errors: JSON | None               # [{row, field, message}]
    created_at, committed_at
    # Rollback: COMMITTED → ROLLED_BACK soft-deletes every row stamped with this batch id.

class ImportRow(Base):                # import_rows — staged, pre-commit (lets the wizard preview + validate)
    id, firm_id, batch_id (FK)
    raw: JSON                         # original row
    mapped: JSON                      # normalised to canonical fields
    dedupe_match_id: int | None       # matched existing candidate/company id
    decision: str                     # "insert" | "update" | "skip" (user-overridable in step 3)
    valid: bool; row_errors: JSON | None
```

### 5.4 Email / OAuth / integrations

```python
class EmailAccount(Base):             # email_accounts — a user's connected mailbox (per-user, firm-scoped)
    id, firm_id, user_id (FK)
    provider: EmailProvider
    email_address: str
    access_token_enc: Text            # Fernet-encrypted (crypto.py) — NEVER serialised to client
    refresh_token_enc: Text
    token_expires_at: datetime
    scopes: str
    sync_cursor: str | None           # Gmail historyId / Graph deltaLink — incremental inbox sync
    sync_state: str                   # "OK" | "REAUTH_REQUIRED" | "DISABLED"
    last_synced_at: datetime | None
    is_send_enabled, is_sync_enabled: bool
    created_at, updated_at
    __table_args__ = (UniqueConstraint("user_id", "provider", "email_address"),)

class EmailMessage(Base):             # email_messages — system-of-record for every touch email
    id, firm_id
    mandate_id (FK), company_id (FK | None), contact_id (FK | None)
    account_id: FK | None             # which mailbox; null for MOCK
    direction: EmailDirection
    status: EmailStatus
    provider_message_id, provider_thread_id: str | None   # for sync dedupe + threading
    to_addrs, cc_addrs: JSON
    subject: str; body_html, body_text: Text
    template_id: FK | None
    scheduled_for: datetime | None    # SCHEDULED send time (IST-aware)
    sent_at, received_at: datetime | None
    outreach_event_id: FK | None      # the auto-logged event (5.x) — the link that closes the loop
    created_by_id (FK), created_at, updated_at
    __table_args__ = (UniqueConstraint("firm_id","provider_message_id"),)  # idempotent sync
```

**The loop that satisfies the user's requirement:** both *send-from-platform* and *inbox-sync* end by creating exactly one `OutreachEvent` (the existing append-only primitive) and stamping `EmailMessage.outreach_event_id`. The cadence engine sees a normal event and advances/stops as usual. See §8.4.

### 5.5 AI jobs & suggestions

```python
class AIJob(Base):                    # ai_jobs — one row per LLM invocation, for audit + cost + caching
    id, firm_id, requested_by_id (FK)
    type: AIJobType; status: AIJobStatus
    subject_type, subject_id          # polymorphic target (mandate/candidate/company/contact)
    input_hash: str (idx)             # sha256 of prompt inputs → cache key (skip re-spend)
    provider: str; model: str         # "mock" | "anthropic:claude-opus-4-8" ...
    prompt_tokens, completion_tokens, cost_usd: nullable
    result: JSON | None; error: str | None
    created_at, completed_at

class AISuggestion(Base):             # ai_suggestions — surfaced, human-in-the-loop
    id, firm_id, job_id (FK)
    type: AIJobType
    subject_type, subject_id
    payload: JSON                     # {score, rationale, fields:{...}, draft:{subject,body}, ...}
    state: SuggestionState = PROPOSED
    decided_by_id: FK | None; decided_at: datetime | None
    created_at
```

### 5.6 Templates, activity, notifications, saved searches

```python
class EmailTemplate(Base):            # email_templates (P-02)
    id, firm_id, created_by_id
    name: str; subject: str; body_html: Text
    merge_fields: JSON                # detected {{company_name}}, {{contact_name}}, {{first_name}}, {{sender_name}}...
    is_shared: bool = True            # firm-wide vs personal
    archived_at, created_at, updated_at

class ActivityEvent(Base):            # activity_events (P-04) — a unified, queryable feed (distinct from OutreachEvent)
    id, firm_id, mandate_id (FK | None), actor_id (FK | None)
    verb: str                         # "created_company" | "logged_outreach" | "pushed_candidate" | "imported" | "ai_ranked" ...
    object_type, object_id
    meta: JSON | None
    created_at (idx)
    # Written by a tiny activity.log(...) helper called from services; NOT user-editable.

class Notification(Base):             # notifications (P-03)
    id, firm_id, user_id (FK)
    type: NotificationType
    title, body: str; link: str | None
    read_at: datetime | None
    created_at (idx)

class SavedSearch(Base):              # saved_searches (S-03 reuse + cockpit saved views, §10.5)
    id, firm_id, user_id, mandate_id (FK | None)
    name: str; criteria: JSON
    created_at, updated_at

class ReportSubscription(Base):       # report_subscriptions (§11.3, research delta #5)
    id, firm_id, user_id (FK), mandate_id (FK | None)   # null = firm-wide report
    cadence: str                      # "daily" | "weekly" (cron-ish); next_run_at computed
    format: str                       # "xlsx" | "pdf" | "inline"
    recipients: JSON                  # extra emails beyond the owner
    next_run_at, last_sent_at: datetime | None
    is_active: bool = True
    created_at, updated_at
```

### 5.7 Migrations & backfill

- **One Alembic migration per phase**, never a mega-migration. Each is additive (new tables / nullable columns) so it's safe on the seeded dev DB and on prod Postgres.
- **Backfill on the project layer (Phase 8):** set `mandate.stage` from existing `MandateStatus` (ACTIVE→IN_PROGRESS, ON_HOLD→ON_HOLD, CLOSED→WON, TERMINATED→ABANDONED). Seed `UserProjectPref.last_opened_at` lazily (first open writes it).
- **Seed script extensions:** extend `app/seed/seed.py` per phase — pool candidates (≈300, with 8 deliberate dupes against existing companies for dedupe demos), 2–3 import batches in mixed states, a handful of `EmailMessage` (MOCK) with linked events, 1 connected MOCK mailbox per analyst, a few AI suggestions in PROPOSED state, sample templates, and notifications. The whole expansion must be demoable with `seed --reset` and **no secrets**.

---

## 6. The AI layer — provider-agnostic, key-optional

This is the spine that makes "build it robust now, plug the key in later" true.

### 6.1 The abstraction (`integrations/base.py`)

```python
class LLMProvider(Protocol):
    name: str
    async def complete(self, *, system: str, messages: list[dict],
                       schema: dict | None = None, max_tokens: int = 1024) -> LLMResult: ...
    # LLMResult = {text|json, model, prompt_tokens, completion_tokens, cost_usd}
```

`services/ai.py` never imports a vendor SDK. It builds typed prompts, calls `registry.llm()`, persists an `AIJob` + `AISuggestion`, and returns suggestions. Swapping providers touches only `registry.py` + an env var.

### 6.2 Mock mode (no key — the default today)

`integrations/llm/mock.py` returns **deterministic, schema-valid** output derived from the input (hash-seeded), so the UI, persistence, accept/reject flow, tests, and demos all work with zero secrets:

- **RANK_CANDIDATES** → score 0–100 from a transparent heuristic (sector match + geo match + size proximity to the mandate thesis + source_quality weight) and a templated rationale. This is genuinely useful, not noise — it's the same scoring `services/sourcing.py` uses for non-AI ranking, surfaced as "AI" until the real model is wired.
- **ENRICH** → fills missing firmographics from `enrichment/mock.py` (deterministic synthesis from name/domain).
- **DRAFT_EMAIL** → renders a real merge-field template populated from company/contact, with thesis-aware framing.
- **THESIS_MATCH / DEDUPE_ASSIST** → reuse `dedupe.py` + the heuristic scorer.

> Because mock output is the same *shape* as real output, **nothing downstream knows or cares** which provider ran. Phase 13's "wire the real key" is: implement `anthropic.py`, set `AI_PROVIDER=anthropic`, drop the key in `.env`. Done.

### 6.3 Where AI is used

| Job | Trigger | Output (suggestion) | Human step |
|---|---|---|---|
| `RANK_CANDIDATES` (S-07) | "AI rank" on sourcing results | score + rationale per candidate — **signals-based** where data exists: acquisition history, capital deployment, hiring, strategic adjacency (§19.4); falls back to thesis-field match | sort/triage; push winners |
| `THESIS_MATCH` | thesis edited / "find matches" / **new pool entrant (continuous monitor, §7)** | ranked pool subset + auto-tag matches to the thesis | review, shortlist |
| `ENRICH` (S-05) | candidate/company with gaps | proposed field values + confidence | accept-all / per-field accept (enrichment diff UI) |
| `DRAFT_EMAIL` | "Draft with AI" in composer | subject + body using merge fields | edit, then send (auto-logs) |
| `DEDUPE_ASSIST` | import preview / ambiguous match | "likely same as X (0.8)" | confirm merge/insert |
| `COMPANY_SUMMARY` (§19.4) | open a company / "brief me" | one-paragraph brief from fields + timeline + notes | read; optional save to notes |
| `RELATIONSHIP_INTEL` (§19.4-#2) | open a company/contact | warm-path summary + relationship-strength rationale over cross-mandate history | review before outreach |

### 6.4 Config & secrets (`integrations/registry.py`)

```
AI_PROVIDER=mock            # mock | anthropic | openai
ANTHROPIC_API_KEY=          # empty today → registry forces 'mock' and logs a one-line notice
AI_MODEL_DEFAULT=claude-opus-4-8
AI_MODEL_CHEAP=claude-haiku-4-5-20251001   # ranking/enrich batch jobs
AI_MAX_USD_PER_DAY=5.0      # circuit-breaker; exceeded → fall back to mock + notify
```

`registry.llm()` resolves at call time: if the selected provider has no key, it transparently downgrades to `mock` and records `provider="mock(fallback)"` on the job — so a missing key degrades gracefully instead of erroring. (See `claude-api` skill for current Claude model IDs, params, tool-use/structured-output, token counting, and caching before implementing `anthropic.py`.)

### 6.5 Guardrails

- **Caching:** `AIJob.input_hash` dedupes identical requests within a TTL — never pay twice for the same ranking.
- **Cost ceiling:** per-firm daily USD cap (`AI_MAX_USD_PER_DAY`); breaching it falls back to mock and raises a notification.
- **Audit:** every call is an `AIJob` row (who/what/model/tokens/cost). Every surfaced item is an `AISuggestion` with accept/reject provenance.
- **Firm-scoping & PII:** prompts only ever include the requesting firm's data; never cross-firm. Strip secrets; send only the fields a job needs. Document a "no training on our data" expectation in the provider config notes.
- **Determinism where it matters:** AI never sets status, never writes cadence, never hard-commits a field — it proposes; a human/`accept` endpoint commits.

---

## 7. Sourcing Layer (S-01 … S-07)

The loop: **ingest → normalise/dedupe → pool → search → push to Master List → enrich → (pluggable feeds) → AI rank.**

### 7.1 Pool & push (S-04)
- The **pool is firm-level** (`SourcingCandidate`). Searching/filtering happens against the pool, optionally scoped to a project's thesis.
- **Push** (`POST /sourcing/candidates/{id}/push` body `{mandate_id}`): inside one transaction — create a `Company` (copy fields, `source_candidate_id` set, `source` preserved), create its `AWAITING_INITIAL` schedule (reuse the exact Phase-3/4 path so the cadence contract holds), copy `CandidateContact`s → `Contact`s (primary preserved), run cross-mandate dedupe and attach advisory warnings, write a `CandidatePush` + `ActivityEvent`, set candidate `status=PUSHED`. Idempotent per `(candidate, mandate)`.
- Bulk push: `POST /sourcing/push-batch {candidate_ids[], mandate_id}`.

### 7.2 Normalise & dedupe (shared, S-01)
Promote the MVP's `cross_mandate.py` helpers into `services/dedupe.py` as the single normaliser used by import, sync, and push:
- `normalise_name()` (strip legal suffixes/punctuation/case), `extract_domain()` (registrable domain).
- `match(candidate_like) -> MatchResult` returns best existing candidate/company with a confidence score (exact domain = high; normalised-name = medium; fuzzy token ratio threshold = low). Used to set `ImportRow.dedupe_match_id` and to power `DEDUPE_ASSIST`.
- The existing per-mandate duplicate **warning** behaviour is unchanged; this just centralises the matching primitive.

### 7.3 Search (S-03)
`GET /sourcing/candidates?q&sector&geography&type&size_band&source&source_quality&status&mandate_id&sort&page&page_size` → the §6.2-style summary envelope (counts by status/source quality over the full filtered set). `sort=ai_score` triggers/reads the latest `RANK_CANDIDATES` suggestions for the result set. Filters are storable as `SavedSearch`.

### 7.4 Enrichment (S-05)
`POST /sourcing/candidates/{id}/enrich` (and `/companies/{id}/enrich`) → runs an `ENRICH` AIJob, returns an `AISuggestion` with proposed field values + confidence. The **enrichment-diff UI** shows current vs proposed per field; analyst accepts all / per-field / none. Accepted values write to columns; the raw payload is retained in `enrichment` JSON for provenance. **Never overwrite a non-null analyst-entered field without explicit accept.**

### 7.5 Pluggable external sources (S-06 — architecture only)
`EnrichmentProvider` / a future `SourceFeedProvider` protocol with a `mock` impl and a documented `clearbit_like.py` stub. Adding a real feed (e.g. Inven) later = implement the protocol + register it; the pool/search/push flow is untouched. **We do not acquire data; we adapt to it** (PRD §7.2 strategic caution).

### 7.6 AI ranking (S-07)
`POST /sourcing/rank {mandate_id, candidate_ids[]}` → `RANK_CANDIDATES` job → suggestions with score+rationale. In mock mode this is the transparent heuristic (§6.2); flipping `AI_PROVIDER` upgrades it to the model with no UI change.

---

## 8. Email & scheduling integration (P-01, P-03)

> **This is the keystone adoption feature** (§19.1): research is unanimous that manual data entry is the #1 reason dealmakers abandon CRMs, and auto-capture is the single biggest driver of adoption. So **auto-capture is the default logging path**; the manual "Log outreach" dialog is the fallback. Treat this section as the product's stickiness engine, not a "suggested" add-on.

Satisfies the user's two explicit asks: **(1)** send a scheduled email from the platform and have it auto-log; **(2)** if a touch was sent from the user's own inbox (e.g. the partner emailed the target directly), auto-log it for the deal/analyst.

### 8.1 OAuth sign-in + mailbox connect (S-«auth», user req: "login with gmail or company account")
- Add **Google** and **Microsoft** OAuth: `GET /auth/oauth/{provider}/start` → consent → `GET /auth/oauth/{provider}/callback`. Two modes:
  - **Sign-in/up:** first-time OAuth with a verified email either signs into an existing user (match by email) or, for a brand-new firm, runs the same `signup` path (creates firm + PARTNER). Domain-based firm matching is **opt-in/manual-approve** to avoid stranger-joins-your-firm bugs.
  - **Connect mailbox:** an already-logged-in user grants `gmail.send`+`gmail.readonly` (or Graph `Mail.Send`+`Mail.Read`), creating an `EmailAccount`. Tokens stored **encrypted** (`crypto.py`).
- Password auth stays; OAuth is additive. Cookie session model is unchanged.
- **Mock provider** lets you build/test the entire connect→send→sync UX with **no Google/MS app** by selecting `EmailProvider.MOCK`.

### 8.2 Compose & send (P-01)
`email-composer.tsx`: pick template (P-02) or "Draft with AI" (§6.3), merge fields auto-fill from the selected company/contact, choose **Send now** or **Schedule for** a datetime (IST). `POST /email/messages` creates an `EmailMessage` (`DRAFT`→`SCHEDULED`/`SENDING`). A worker (`send_scheduled_email`) sends via the user's `MailProvider` at the due time.

### 8.3 Auto-log on send
On successful send, in the same task: create an `OutreachEvent` (`INITIAL_EMAIL` if the schedule is `AWAITING_INITIAL`, else `FOLLOW_UP`), link `EmailMessage.outreach_event_id`, update `contact.last_contact_date`, write an `ActivityEvent`. **This reuses the exact event path the manual dialog uses** — so cadence activates/advances identically. No new cadence code.

### 8.4 Inbox sync auto-log (P-01, user req: "if already sent for that partner … automatically log for the analyst")
Worker `sync_mailbox` (incremental via Gmail `historyId` / Graph delta, cursor in `EmailAccount.sync_cursor`):
1. Pull new **sent** messages (and replies) since the cursor.
2. For each, extract recipient/sender addresses + domains; **match** to a `Contact`/`Company` (by email, then domain via `dedupe.match`) and thus to a mandate. Ambiguous matches (a domain on multiple mandates) surface as a **review queue**, not a silent guess.
3. On confident match, upsert an `EmailMessage` (`direction=OUTBOUND/INBOUND`, `status=SENT/RECEIVED`, idempotent on `provider_message_id`) and **auto-log an `OutreachEvent`** attributed to the deal — even though it was sent from the partner's own client. An inbound reply logs a `RESPONSE` event → cadence stops, exactly per the MVP rules.
4. Idempotency: the unique `(firm_id, provider_message_id)` constraint means re-syncing never double-logs.

> This is the feature's whole point: the platform reflects reality whether the email was sent *through* it or *around* it. The analyst's tracker stays correct without manual logging.

### 8.5 Mock email transport
`mail/mock.py` "sends" by writing the `EmailMessage` as `SENT` and creating the linked event — no network. `sync_mailbox` in mock mode replays a small scripted set of "received from the connected inbox" messages from the seed so the auto-log demo works offline.

### 8.6 Reminders & digest (P-03)
- **In-app `Notification`s** generated when items cross due/overdue (driven by the existing cadence queues) and on import/AI completion.
- **Daily digest email** (`digest.py`, scheduled worker, IST morning): per-analyst summary of due/overdue/needs-initial + new responses. Sent via the connected mailbox or a system transport; in mock mode it renders to a notification + logs the HTML. Respect a per-user `digest_opt_in`.

---

## 9. Data ingest — Excel/CSV import wizard (S-01, S-02, P-06)

The user's "upload our real-time company data — excels" rail. A guided, reversible 4-step flow over the §5.3 staging tables.

1. **Upload** — `POST /imports` (multipart, `.xlsx`/`.csv`, `kind`, optional `target_mandate_id`). `ingest.py` parses with **openpyxl/pandas**, detects headers, creates `ImportBatch(UPLOADED)` + `ImportRow`s (raw).
2. **Map columns** — auto-suggest `column_map` against the canonical dictionary (Appendix B) by header fuzzy-match; analyst confirms/overrides. `PATCH /imports/{id}/mapping`.
3. **Validate & preview** — `POST /imports/{id}/validate`: normalise each row, run `dedupe.match` → set `dedupe_match_id` + `decision` (insert/update/skip), validate types/required, collect `row_errors`. UI shows a preview grid with dupe flags and lets the analyst flip per-row decisions. Status → `READY`.
4. **Commit** — `POST /imports/{id}/commit` (background for large files): insert candidates/companies/contacts stamped with `import_batch_id`; "update" decisions patch only empty fields (provenance rule). Status → `COMMITTED`; notification on done.

- **Rollback:** `POST /imports/{id}/rollback` soft-deletes everything stamped with the batch → `ROLLED_BACK`. Makes imports safe to trust.
- **Onboarding wizard (P-06)** is the same flow pre-seeded with the firm's existing-tracker layout (the live Master List / Contact List / Email Schedule columns the PRD documents), so a firm migrates its spreadsheets in minutes — the "near-zero switching cost" GTM lever.

---

## 10. Personas, view model & the projects-first workspace

### 10.0 Two personas, one dataset, role-aware defaults

The PRD (§3) is explicit: the **daily user (analyst)** and the **economic buyer (partner/MD)** are different people. We serve both from the *same* project objects with different default lenses — **not two products**.

- **Analyst / Associate = operator.** Lives *inside one project at a time*. Default landing = their current/pinned project's **worklist cockpit** (§10.5). Cares about: not missing a follow-up, logging fast, working hot leads.
- **Partner / MD = overseer.** Starts *at the top*. Default landing = the **firm portfolio dashboard** (§10.6) with per-analyst accountability + firm-wide duplicate alerts. Drills into any project to get the *same* cockpit, read-mostly.
- **ASSOCIATE defaults to operator** (hands-on). One per-firm setting can flip associates to overseer if a firm treats them as oversight. *(Open assumption — change here if wrong.)*

Role-aware routing: `useAuth().role` decides the post-login redirect and which nav group is emphasized. Both roles can reach every surface; only the *default* landing and a few partner-only panels differ (reuse the MVP's existing partner gates — by-analyst analytics is already partner-only).

| Surface | Route | Analyst / Associate | Partner / Exec |
|---|---|---|---|
| Firm portfolio dashboard | `/dashboard` | available, secondary | **default landing** |
| Projects index | `/projects` | only assigned/created | **all** projects + health signals |
| Per-project cockpit | `/projects/[id]` | **default landing**, full actions | drill-in, read-mostly |

### 10.1 Mandate-type awareness — buy-side / sell-side / capital-raise

`MandateType` is not a tag; it **flips what the analyst is doing**, so the workspace relabels and re-emphasizes itself (the model already encodes it: `MandateType` × `CompanyType`):

| Type | The list is | Analyst asks | "Add" button | Emphasized columns | Default `CompanyType` |
|---|---|---|---|---|---|
| **SELL_SIDE** | Buyers / investors | "Who would acquire our client?" | + Add buyer | acquisition appetite, relevant investments, dry powder | BUYER |
| **BUY_SIDE** | Targets | "Who fits the acquisition thesis?" | + Add target | revenue, growth, headcount, owner willingness | TARGET |
| **CAPITAL_RAISE** | Investors | "Who would fund our client?" | + Add investor | fund stage/size, sector focus, check size | INVESTOR |

**Implementation:** a single `useMandateVocab(type)` hook returns `{ noun, addLabel, defaultCompanyType, emphasizedColumns, sourcingPreset }`. The cockpit, the Add dialog, the sourcing search presets, and column visibility all read from it — **one view, type-aware, no forked screens**. The project-card side-tag (SELL / BUY / CAP) already derives from `MandateType`. Sourcing presets differ accordingly: sell-side seeds strategics + PE with relevant portfolios; buy-side seeds targets by sector/size/geo thesis.

### 10.2 Project index (`/projects` — first mockup)
- Header "Projects" + subtitle, **New project** (amber CTA), search.
- **Pinned project** section (per-user pin from `UserProjectPref`), then a card grid.
- **`project-card.tsx`:** `stage` badge (IN PROGRESS / ABANDONED / ON HOLD / WON, §3.2 status colours), avatar monogram, name, "Open project" link, side-tag (SELL/BUY/CAP from `MandateType`), pin toggle (top-right). Cards link to `/projects/[id]`.
- **Scope:** analyst sees only assigned/created projects; **partner sees all, with per-card health signals** (overdue count, last-activity age, lead owner). Reuse `visible_mandate_ids`.

### 10.3 Project switcher (`project-switcher.tsx`)
- The "CURRENT PROJECT" dropdown in the sidebar (mockup). Lists visible projects, sets the active project (writes `last_opened_at`), and **scopes the nav** (Dashboard/Companies/Sourcing/Timeline become the active project's). Persist selection per-user; default to most-recently-opened or pinned.

### 10.4 Sidebar nav (role-aware)
`Projects · Dashboard · Companies · Sourcing · Templates · Settings`. Dashboard/Companies/Sourcing resolve to the **current project** when one is selected, with a firm-wide toggle. For **partners**, the firm Dashboard is pinned at top; for **analysts**, the current-project cockpit is. Keep the §3.2 amber active-indicator treatment from `UI_ENHANCEMENT_PLAN.md`.

### 10.5 Analyst workspace — the split-pane worklist cockpit (`/projects/[id]`)

The analyst's **home inside a project** and the centerpiece of this whole chapter. It replaces the MVP's plain `/companies` table for in-project work. The analyst is an operator under deadline managing 50–150 companies on a fixed cadence; the view is a Superhuman/Linear-style **cockpit**, cadence-first, with a preview pane so they act without losing their place.

```
┌─ ABC Industrials  [SELL-SIDE] · Buyer outreach ──────────────────────────────────┐
│ ● 3 overdue   ◐ 5 due today   ○ 12 this week   ◇ 8 awaiting first email           │
│ [ Worklist ▾ ] [ Board ] [ Table ]      🔍 filter  ⌨ keys  ⊕ Add buyer  ⤓ Import  │
├───────────────────────────────────┬───────────────────────────────────────────────┤
│ OVERDUE (3)                        │  Vertex Capital                  [BUYER]      │
│ ● Vertex Capital  2d  ▸ contacted  │  Status: Contacted · POC: You · 3rd follow-up │
│ ● Helios PE       1d  ▸ contacted  │  Next due: today                              │
│ ● Northstar       4d  ▸ RESPONDED  │  📇 R. Mehta — MD  ★primary      ✉  ☎         │
│ DUE TODAY (5)                      │  🕑 Apr 12 Initial · Apr 26 FU#1 · May 10 FU#2 │
│ ◐ Apex Holdings   0d  ▸ contacted  │  ⚠ also a buyer on "Project Helios" (dupe)    │
│ ◐ Blue Owl        0d  ▸ contacted  │  ┌─────────────────────────────────────────┐ │
│ THIS WEEK (12)  ○ …                │  │ ✉ Log / Send   ⏱ Schedule   ✓ Mark resp. │ │
│ AWAITING FIRST (8)  ◇ Kinetic Auto │  └─────────────────────────────────────────┘ │
└───────────────────────────────────┴───────────────────────────────────────────────┘
```

**Three lenses, same data, toggled top-right; default = Worklist:**
- **Worklist (default):** left = triage list grouped by cadence urgency (Overdue → Due today → This week → Awaiting first email), mirroring the engine exactly. Right = **preview pane** (`preview-pane.tsx`): company fields, contacts, append-only timeline, inline cross-mandate **dupe guard**, and one-click **Log / Send / Schedule / Mark responded** — act inline, never leave the list. This split-pane is the single biggest speed win.
- **Board (`board-view.tsx`):** kanban by `CompanyStatus` (Not contacted → Contacted → Responded → Interested → Declined/Bounced) for "where does everything stand." *(Phased: ships after Worklist+Table — see Phase 8 / Phase 16.)*
- **Table:** the power-grid — sort / filter / inline-edit, the spreadsheet replacement; reuses the MVP `DataTable`.

**Intelligence in the preview pane (from research, §19):**
- **Relationship panel (`X-02`):** "who at our firm already knows this company/contact, on which mandate, last touch, outcome" — surfaces the cross-mandate shared-memory we already store as *warm-intro paths*, with a lightweight **relationship-strength score** (touch count × recency × response). Optional AI `RELATIONSHIP_INTEL` upgrades the rationale. This is the market's #1 analyst ask after auto-capture.
- **"Going cold" flag (`A-03`):** a company with email silence beyond a threshold (no event in N days while ACTIVE) gets an amber "cooling" marker — derived from the event log, no AI needed.
- **AI brief (`COMPANY_SUMMARY`):** a "brief me" one-paragraph summary from fields + timeline + notes.

**Big-org affordances (essential at 150-row volume):** bulk-select → bulk log / assign / push-from-sourcing; **saved views** ("my hot leads", "TMT buyers not yet contacted", "overdue & assigned to me", "going cold"); **POC column + "assigned to me" filter** (multiple analysts per mandate); **keyboard-first** (`j/k` move, `e` log, `s` schedule); density toggle (comfortable / compact). All firm + visibility scoped.

### 10.6 Executive / partner portfolio (`/dashboard` at firm scope — overseer home)

The partner's default landing — mockup #2 as a **cross-project roll-up**, plus oversight panels the analyst doesn't get (validated by §19.3):
- **KPI roll-up across all projects:** active projects, targets in outreach, due follow-ups, responses received (count-up cards).
- **Conversion funnel + stage conversion rates** (`A-01`): contacted → responded → interested → progressed, with the rate between each stage — the screening-quality / negotiation-strength signal partners explicitly want (§19.3). First-class panel, not buried in analytics.
- **Per-analyst accountability:** overdue count + response rate by owner (extends the existing partner-only by-analyst analytics) — "who's behind."
- **"Deals going cold" watchlist** (`A-03`): projects/targets with email silence past threshold — "deals going cold based on email silence," a named partner need (§19.3).
- **Firm-wide duplicate alerts:** the cross-mandate dupe service surfaced as a watchlist — the partner's "no embarrassing double-touch" guarantee, their #1 fear in the brief.
- **Project health table:** every project with stage, due/overdue counts, last activity, lead owner → click drills into that project's cockpit.
- **Scheduled report delivery:** subscribe to a weekly/daily status report auto-emailed to the partner's inbox (§11.3) — partners "want live reports scheduled for delivery to their inbox" (§19.3).

### 10.7 Per-project dashboard (shared overview tab)

Mockup-#2's layout scoped to one mandate — KPI strip, Priority Notifications (urgent cadence items, HIGH/MEDIUM/LOW from days-remaining), Outreach Distribution donut (Contacted vs Responded vs No-response), Company Outreach Timeline (click a company → full-screen append-only event log + synced `EmailMessage`s). Both roles see it as the project's **Overview** tab, alongside the cockpit (§10.5). Backend: extend the analytics endpoints to accept `mandate_id` (`/analytics/overview` already does); both dashboards share components, only the scope param differs.

---

## 11. Suggested features

### 11.1 Templates (P-02)
`/templates` CRUD; `templates.py` renders `{{merge_fields}}` (company_name, contact_name, first_name, sender_name, mandate_name, …) with safe escaping and missing-field warnings. Used by the composer and AI draft.

### 11.2 Activity timeline (P-04)
`activity.py` writes `ActivityEvent`s from services (create/import/push/log/ai/enrich). `GET /projects/{id}/activity` → chronological feed for partner oversight + audit. Distinct from the outreach event log (that's per-company touches; this is per-project operational history).

### 11.3 Export + scheduled delivery (P-05, §19.3)
`export.py`: `GET /projects/{id}/export?format=xlsx|pdf` → Master List + status + cadence as a clean client-ready report (openpyxl for Excel, weasyprint/reportlab for PDF). Streamed download; firm/visibility-scoped.
**Scheduled delivery (research delta #5):** a `report_subscription` (cron-like cadence + recipients + scope) lets a partner auto-receive the status report by email — reuses the `digest.py` worker + the export renderer. Partners "want live reports scheduled for delivery to their inbox" (§19.3). Mock transport renders it to a notification offline.

---

## 12. API surface (new routers)

```
# Projects (alias over mandates service)
GET    /projects                      list (visibility-scoped) + per-project stats
POST   /projects                      create (ANALYST/ASSOCIATE/PARTNER) → auto-assign creator
GET    /projects/{id}                 detail + stage + thesis
PATCH  /projects/{id}                 edit (stage, thesis, sector/geo/size)
POST   /projects/{id}/pin             toggle per-user pin (UserProjectPref)
POST   /projects/{id}/open            set current project (last_opened_at)
GET    /projects/{id}/activity        P-04 feed
GET    /projects/{id}/export          P-05 (xlsx|pdf)

# Sourcing
GET    /sourcing/candidates           search + summary envelope (S-03)
POST   /sourcing/candidates           create one (manual add to pool)
GET    /sourcing/candidates/{id}
PATCH  /sourcing/candidates/{id}
POST   /sourcing/candidates/{id}/push {mandate_id}        (S-04)
POST   /sourcing/push-batch           {candidate_ids[], mandate_id}
POST   /sourcing/candidates/{id}/enrich                   (S-05)
POST   /sourcing/rank                 {mandate_id, candidate_ids[]} (S-07)
GET/POST/DELETE /sourcing/saved-searches

# Imports (S-01/02, P-06)
POST   /imports                       upload → staged batch
PATCH  /imports/{id}/mapping
POST   /imports/{id}/validate
GET    /imports/{id}                  status + preview rows + errors
POST   /imports/{id}/commit
POST   /imports/{id}/rollback

# Email & integrations (P-01)
GET    /auth/oauth/{provider}/start | /callback
POST   /integrations/mailbox/connect/{provider}
GET    /integrations/mailbox          status (sync_state, last_synced_at)
POST   /integrations/mailbox/sync     trigger incremental sync
DELETE /integrations/mailbox/{id}     disconnect (revoke + wipe tokens)
POST   /email/messages                compose: send-now | schedule  (auto-logs)
GET    /email/messages?company_id|mandate_id
GET    /email/sync-review             ambiguous-match queue (8.4)
POST   /email/sync-review/{id}/resolve

# AI / templates / notifications
GET    /ai/jobs/{id}                  status/result (polling)
GET    /ai/suggestions?subject_type&subject_id
POST   /ai/suggestions/{id}/accept | /reject
GET/POST/PATCH/DELETE /templates                          (P-02)
GET    /notifications | POST /notifications/{id}/read     (P-03)
```

All endpoints: firm-scoped + visibility-scoped, soft-delete aware, summary-envelope for lists, partner-only gates only where the MVP already gates (archive, cross-user assignment, by-analyst analytics, firm settings).

---

## 13. Frontend routes & screens (summary)

| Route | Screen | PRD |
|---|---|---|
| `/dashboard` | **Exec/partner firm portfolio** (roll-up + per-analyst + dupe alerts) | §10.6 |
| `/projects` | Project index + pinned + new-project + switcher source | mockup #1 |
| `/projects/[id]` | **Analyst cockpit** (Worklist/Board/Table + preview pane), type-aware; Overview tab = per-project dashboard | §10.5/10.7, mockup #2 |
| `/projects/[id]/sourcing` | Pool search scoped to thesis + AI rank + push | S-03/04/07 |
| `/projects/[id]/timeline` | Activity feed | P-04 |
| `/sourcing` | Firm-level pool + search + enrich | S-03/05 |
| `/import` | 4-step import wizard | S-01/02, P-06 |
| `/templates` | Email templates | P-02 |
| `/settings/integrations` | Connect Gmail/Outlook · AI key status · source feeds | P-01, §6.4 |
| (composer modal) | `email-composer.tsx` send/schedule + AI draft | P-01 |

Reuse all `UI_ENHANCEMENT_PLAN.md` tokens (Obsidian Amber, Cormorant/Outfit/JetBrains Mono, amber-only-accent, motion). New components inherit the design system; no new color decisions.

---

## 14. Build phases (8–16)

Each phase is a vertical slice: schema → service → API (+ tests) → UI (+ tests) → `PROGRESS.md`. Estimates assume the MVP velocity already demonstrated.

### Phase 8 — Projects-first workspace, role-aware views & type-aware cockpit `~5d`
The biggest UX slice; delivers both mockups + the analyst cockpit. Sub-parts:
- **8a — Project layer & nav:** extend `Mandate` (stage/thesis/sector/geo/size), `UserProjectPref`, project alias router, per-user pin & current-project, **analyst can create** (auto-assign creator), project index (`project-card`) + switcher, **role-aware default landing** (`use-role-home`: analyst → cockpit, partner → portfolio; ASSOCIATE = operator default).
- **8b — Type-aware analyst cockpit (§10.5):** `worklist-cockpit` + `preview-pane` + `lens-switcher` with **Worklist (default) + Table** lenses; `use-mandate-vocab` relabels noun/add-button/columns/default-type by buy-side/sell-side/cap-raise; inline log/send/schedule reuse the MVP event path; "assigned to me" + saved views; keyboard `j/k/e/s`. *(Board lens deferred to Phase 16.)*
- **8c — Per-project dashboard (§10.7) + exec portfolio (§10.6):** scope analytics endpoints by `mandate_id`; partner `/dashboard` gains **conversion funnel + stage conversion rates** (research delta #4), per-analyst accountability, firm-wide duplicate watchlist, project-health table; cockpit preview pane gains the **relationship panel + strength score** (`X-02`, research delta #2 — derived from existing cross-mandate memory, no AI needed).

**Done when:** analyst logs in → lands on their current/pinned project cockpit → triages the Worklist, opens the preview pane, logs a touch inline (cadence advances) without leaving the list → switches to Table lens; a sell-side project says "Buyers / + Add buyer", a buy-side project says "Targets / + Add target". Partner logs in → lands on the firm portfolio → sees overdue-by-analyst + a cross-mandate dupe alert → drills into a project cockpit read-mostly. `stage↔MandateStatus` mapping stops cadence on ABANDONED/WON; migration backfills `stage`. pytest + Vitest green; Playwright: analyst create→pin→cockpit→log; partner portfolio→drill-in.

### Phase 9 — Ingest normaliser + sourcing pool (no UI AI yet) `~3d`
`services/dedupe.py` (promote cross_mandate), `SourcingCandidate`/`CandidateContact`/`CandidatePush`, pool CRUD + search (S-03) + **push-to-Master-List** (S-04, reuses cadence path), seed ≈300 candidates w/ dupes.
**Done when:** search/filter the pool with summary envelope; push a candidate → a Company + AWAITING_INITIAL schedule + copied contacts + cross-mandate warning + `CandidatePush`; idempotent; candidate→PUSHED. Tests cover push transaction + dedupe.

### Phase 10 — Import wizard (CSV/Excel) `~3d`
`ingest.py`, `ImportBatch`/`ImportRow`, 4-step API, wizard UI, rollback. (S-01/02, P-06)
**Done when:** upload a sample `.xlsx` → auto-mapped → validate shows dupes/errors → commit inserts stamped rows → rollback soft-deletes them. Onboarding preset for the firm's tracker layout. Tests: parse, mapping, dedupe decisions, commit/rollback.

### Phase 11 — AI layer (mock) end-to-end `~4d`
`integrations/base+registry`, `llm/mock`, `enrichment/mock`, `services/ai.py`, `AIJob`/`AISuggestion`, accept/reject; **signals-based** ranking (S-07, delta #7) + enrichment (S-05) + thesis-match wired into sourcing; plus **`COMPANY_SUMMARY`** brief (delta #8), **`RELATIONSHIP_INTEL`** rationale upgrade on the §8c relationship panel (delta #2), and **thesis monitor** — `THESIS_MATCH` auto-runs on new pool entrants and tags matches to active theses (delta #6). Cost/cache/audit guardrails.
**Done when:** "AI rank" sorts pool results by score+rationale (signals where data exists, else thesis-field match); "Enrich" proposes fields in a diff UI, accept writes columns + keeps provenance; "Brief me" returns a one-paragraph summary; importing a candidate matching an active thesis surfaces it as a suggestion; everything works with **no key**; jobs/suggestions audited; cache prevents re-spend. Tests assert deterministic mock output + accept/reject persistence + no-overwrite rule + thesis-monitor trigger.

### Phase 12 — Email send-from-platform + auto-log (mock transport) `~3d`
`MailProvider` + `mail/mock`, `EmailAccount`/`EmailMessage`, composer (template/AI draft, send-now/schedule), worker `send_scheduled_email`, **auto-log → OutreachEvent** (reuses MVP event path), templates (P-02).
**Done when:** compose → send-now logs an event + advances/activates cadence; schedule → worker sends at due time + logs; merge fields render; all via mock transport, no creds. Tests: send→event linkage, schedule firing, cadence activation via auto-log.

### Phase 13 — Real providers: OAuth + Gmail/Graph + inbox-sync auto-log `~4d`
`oauth/google+microsoft`, `crypto.py` (encrypted tokens), connect-mailbox UX, `mail/gmail`+`graph`, `sync_mailbox` worker (incremental, idempotent), match→auto-log of externally-sent touches, sync-review queue, **wire real Anthropic LLM** (`AI_PROVIDER=anthropic`).
**Done when (with creds in a test env; mock path still green without):** connect a Google mailbox; an email sent from the real client appears as an auto-logged event on the right deal; a reply logs RESPONSE → cadence stops; re-sync never double-logs; ambiguous matches go to review. AI ranking/enrich upgrade to the model with no UI change. Tests: sync idempotency (mock fixtures), match logic, token encryption round-trip.

### Phase 14 — Reminders, digest, "going-cold" & scheduled reports (P-03, deltas #3/#5) `~3d`
`Notification`, in-app bell + list, `digest.py` daily worker, opt-in; **"going-cold" signal** (`A-03`, delta #3) — a derived flag for ACTIVE companies with no event in N days, surfaced in the cockpit (§10.5) + the exec watchlist (§10.6) + as a notification; **scheduled report delivery** (`report_subscription`, delta #5) reusing the export renderer + digest worker.
**Done when:** crossing due/overdue raises notifications; daily digest renders per-analyst due/overdue/needs-initial + new responses; a stalled target shows the "cooling" marker and appears in the partner's going-cold watchlist; a partner can subscribe to a weekly status report auto-emailed (mock-rendered offline, emailed when a mailbox is connected). Going-cold threshold is a firm setting.

### Phase 15 — Activity timeline (P-04) + Export (P-05) `~2d`
`activity.py` + feed UI; `export.py` xlsx/pdf.
**Done when:** project timeline shows create/import/push/log/ai entries chronologically; export produces a clean client-ready Master-List report (both formats), scoped.

### Phase 16 — Board lens, hardening, pluggable-feed stub (S-06), perf & docs `~2d`
**Board (kanban) lens** for the cockpit (§10.5); `SourceFeedProvider`/`EnrichmentProvider` protocols + documented stub (no paid feed), background-queue swap notes (Arq), index/perf pass on pool search + sync, full QA against the §14 checklists, `PROGRESS.md` + README + `.env.example` for every new var, seed covering every feature.
**Done when:** a new external feed *could* be added by implementing one protocol; whole expansion demoable end-to-end with `seed --reset` and zero secrets; all tests green.

> **Sequencing note:** Phases 8–12 deliver the entire product on **mock providers with no secrets** — fully demoable. Phase 13 is the only phase that benefits from real keys, and even it keeps the mock path green so CI never needs a secret.

---

## 15. Testing strategy

- **Backend (pytest):** one test module per new service/router, continuing the MVP pattern (in-memory SQLite, async client). Must-cover invariants: push-to-mandate transaction + cadence contract; import commit/rollback symmetry; **auto-log idempotency** (sync never double-logs — unique `provider_message_id`); enrichment **no-overwrite** rule; AI accept/reject persistence; firm/visibility scoping on *every* new endpoint (the highest-value regression guard); token encryption round-trip; cost-cap fallback to mock.
- **Frontend (Vitest + RTL):** project-card/switcher logic, import-wizard mapping + decision toggles, enrichment-diff accept logic, composer merge-field rendering, notification list.
- **Playwright critical paths:** create-project→pin→open-dashboard; import xlsx→commit→see companies; pool search→AI rank→push→appears in Needs-first-outreach; compose→send→event logged→cadence active; (real-provider path behind an env guard, skipped in CI).
- **Provider contract tests:** the same test suite runs against `mock` and (when configured) `real` providers to prove shape-compatibility.

---

## 16. Security & compliance additions

- **OAuth tokens encrypted at rest** (`crypto.py`, Fernet key from `TOKEN_ENC_KEY`; KMS in prod). Never serialised to the client; `EmailAccount` read schema omits token columns.
- **Least-scope OAuth:** request only `gmail.send`+`gmail.readonly` / `Mail.Send`+`Mail.Read`. Disconnect revokes upstream + wipes columns.
- **Mailbox data is firm-scoped** even though the connection is per-user; sync respects visibility when attributing to mandates.
- **AI prompts never cross firms;** strip PII not needed for the job; honor the daily cost cap; record provider + model on every job for auditability.
- **Import safety:** staged + validated + reversible; commits stamped for rollback; no destructive overwrite of analyst data.
- **Webhooks/callbacks** (OAuth callback, future Gmail push) validate state/nonce + signature; rate-limit sync triggers.
- **Audit log + SOC 2 roadmap (research delta #10, §19.3):** the `ActivityEvent` feed (P-04) doubles as a firm-level **audit trail** (who did what, when) — the accountability + compliance surface the executive buyer expects. Document a SOC 2 readiness path (RBAC ✓, encryption-at-rest for tokens ✓, audit log ✓, access reviews, backups F-04) as a sales-enablement item; full certification is post-PMF, but the controls are designed in now.
- Run the existing `/security-review` before Phase 13 ships (handles real tokens + external calls).

---

## 17. Config / env reference (new vars)

```
# AI
AI_PROVIDER=mock            ANTHROPIC_API_KEY=          OPENAI_API_KEY=
AI_MODEL_DEFAULT=claude-opus-4-8   AI_MODEL_CHEAP=claude-haiku-4-5-20251001
AI_MAX_USD_PER_DAY=5.0

# Email / OAuth (all optional — absence ⇒ MOCK provider)
EMAIL_PROVIDER=mock         # mock | google | microsoft
GOOGLE_CLIENT_ID=  GOOGLE_CLIENT_SECRET=  GOOGLE_OAUTH_REDIRECT=
MS_CLIENT_ID=  MS_CLIENT_SECRET=  MS_TENANT=  MS_OAUTH_REDIRECT=
SYSTEM_FROM_EMAIL=          # for digests when no mailbox connected

# Crypto / workers
TOKEN_ENC_KEY=              # Fernet key (generate per env) — required once any real mailbox connects
QUEUE_BACKEND=inprocess     # inprocess | arq
REDIS_URL=                  # when QUEUE_BACKEND=arq
ENRICHMENT_PROVIDER=mock    # mock | <future feed>
```

Every var has a safe default that keeps the app in **mock mode**, so a fresh clone + `seed --reset` runs the whole expansion with no secrets. Document each in `backend/.env.example` per phase.

---

## 18. Risks & sequencing

| Risk | Mitigation |
|---|---|
| OAuth app approval (Google/MS) is slow | Build entirely on mock providers (Phases 8–12); real OAuth isolated to Phase 13; mock path stays green so nothing blocks |
| LLM cost / latency surprises | Cache by input hash, daily USD cap with mock fallback, cheap model for batch jobs, async jobs (never block a request) |
| Inbox sync double-logging or mis-attribution | Idempotent unique `provider_message_id`; confident-match-only auto-log; ambiguous → review queue, never silent guess |
| "Project = Mandate" confusion | Keep one table; map `stage↔MandateStatus`; UI says "Project" everywhere; documented in CLAUDE.md glossary update |
| Enrichment clobbering analyst data | Suggestions only; no-overwrite-non-null rule; provenance retained; per-field accept |
| Import corrupting the book | Staged + validated + reversible batches; commit stamps every row for one-click rollback |
| Scope creep into a data business | S-06 is an interface + stub only; we integrate, never acquire (PRD §7.2) |

**Recommended order to start:** Phase 8 (gives the user the exact projects+dashboard mockups immediately), then 9–10 (real data in via pool + import), then 11–12 (AI + send, all mock), then 13 (flip on real keys when they arrive), then 14–16 (polish/reporting/hardening).

---

## 19. Market research — what analysts & executives actually need (and what we changed)

Desk research (June 2026) across the incumbents (DealCloud, Affinity, 4Degrees, Grata, Navatar, Midaxo) and the M&A-CRM literature. The goal: validate our deferred features against what the market says day-to-day users and economic buyers demand, and find gaps. Findings below, then the concrete plan deltas.

### 19.1 The one finding that reframes everything: manual entry kills adoption

> "If a CRM depends on manual data entry, adoption will fail… manual data-entry burden is the top-cited reason users abandon the system." A senior dealmaker doing data entry is "an economically irrational use of their time." Firms with high adoption moved to CRMs that **log every email/meeting automatically**. ([MadeMarket](https://www.mademarket.com/blog/how-to-increase-crm-adoption-at-your-investment-bank), [Affinity adoption](https://www.affinity.co/blog/crm-adoption-rates), [4Degrees](https://www.4degrees.ai/blog/investment-banking-crm-guide-the-complete-playbook-for-relationship-driven-dealmakers))

This is the abandonment spiral the PRD warns about, named: *incomplete data → distrust → less usage → worse data*. **Implication:** our email **auto-capture (P-01) is not a "Suggested" nice-to-have — it is the keystone adoption feature**, and the manual "Log outreach" dialog should be the *fallback*, not the primary path. The whole product's stickiness rests on it. We elevate it accordingly.

### 19.2 What ANALYSTS (daily operators) need — evidence

| Need (from research) | Our status | Action |
|---|---|---|
| **Automatic email/calendar capture** (no manual logging) | Planned P-01, was "suggested" | **Elevate to core pillar**; auto-capture = default logging path (§8, §19.1) |
| **Visual pipeline / Kanban with prioritisation & deal scoring** | Worklist + Board lenses planned | Confirmed — keep Worklist default, Board lens (§10.5) |
| **Relationship intelligence / warm-intro paths** ("who at our firm already knows this target") | Partial — cross-mandate contact memory exists, not surfaced as relationships | **NEW: Relationship panel + strength score** (§10.5, §19.4-#2) |
| **Templates + personalised outreach** | Planned P-02 | Confirmed (§11.1, §12 composer) |
| **Tasks, reminders, "deals going cold" alerts** | Planned P-03 (reminders) | **Add "going-cold" signal** (email-silence detection) (§10.5/10.6, §19.4-#3) |
| **Enrichment / firmographics without manual research** | Planned S-05 | Confirmed (§7.4) |
| **Fast, self-serve, no trained admin** | Design intent | **Make an explicit principle** (§3-#16) — our wedge vs DealCloud's months of config |

### 19.3 What EXECUTIVES (economic buyers) need — evidence

> Partners want **real-time pipeline health**, **conversion rates between stages** (screening quality, valuation discipline), total pipeline value & deal count by stage, **accountability** (who's behind; "deals going cold based on email silence"; communication frequency & quality visible at pipeline review), and **scheduled reports auto-delivered to their inbox**. Security (SOC 2, role-based access, encryption) is table-stakes for the buyer. ([InetSoft KPIs](https://www.inetsoft.com/info/mergers-and-acquisitions-dashboard/), [GrowthFactor](https://www.growthfactor.ai/resources/blog/m-a-deal-management-crm), [Affinity auto-capture](https://www.affinity.co/blog/best-crm-automatic-email-meeting-capture))

| Need | Our status | Action |
|---|---|---|
| Real-time portfolio health dashboard | Planned exec portfolio (§10.6) | Confirmed |
| **Conversion funnel + stage conversion rates** | Basic funnel in MVP analytics | **Make first-class on exec dashboard** (§10.6, §19.4-#4) |
| Per-analyst accountability ("who's behind") | Planned (§10.6) | Confirmed |
| **"Deals going cold" / email-silence flag** | Not present | **NEW signal** (§10.6, §19.4-#3) |
| **Scheduled report delivery** (auto-emailed status reports) | Export + digest planned, but on-demand | **Add scheduled delivery** (§11.3, §19.4-#5) |
| Security posture (SOC 2 / RBAC / encryption) | RBAC + token encryption present | **Add audit-log + SOC2 roadmap note** (§16, §19.4-#10) |

### 19.4 AI expectations for 2026 — evidence

> Real AI sourcing identifies companies by **behavioural signals** — acquisition history, capital-deployment patterns, hiring activity, strategic adjacency — *not static attributes*. **Continuous monitoring** auto-scans and **tags new companies to a thesis** automatically. AI **drafts memos/summaries** from emails/notes/decks (80–90% time saved) and scores **relationship strength** to surface dormant relationships matching a mandate. ([PrivSource](https://www.privsource.com/posts/best-ai-tools-for-m-and-a-deal-sourcing-2026), [Navatar](https://www.navatargroup.com/blog/private-equity-and-ma-deal-sourcing/), [EthosData](https://www.ethosdata.com/blog/ai-in-ma-the-5-layer-value-stack-that-will-define-dealmaking-in-2026-2030/), [Grata AI](https://grata.com/technology/ai))

### 19.5 Competitive positioning — evidence

> **DealCloud:** powerful but heavy — months of configuration, external consultants, dedicated admins; AI bolted on. **Affinity:** auto-capture from day one, 80% of firms live in <60 days, self-serve, relationship-led. **Our wedge:** affordable, M&A-native *outreach* for boutiques — fast onboarding, zero-admin, near-zero switching cost. ([Affinity vs DealCloud](https://www.affinity.co/comparison/affinity-vs-dealcloud), [4Degrees alternatives](https://www.4degrees.ai/blog/affinity-dealcloud-or-4degrees--which-crm-is-right-for-your-firm)) — reinforces the **import wizard (P-06)** as the #1 GTM lever and **self-serve simplicity** as a design constraint.

### 19.6 Plan deltas (what research changed) — net new / elevated features

| # | Delta | Type | Where | PRD/Phase |
|---|---|---|---|---|
| 1 | **Email auto-capture is the keystone** — default logging path; manual is fallback | ELEVATE | §8, §19.1 | P-01 / 12–13 |
| 2 | **Relationship-intelligence panel + strength score** (warm-intro paths from cross-mandate memory; AI-optional `RELATIONSHIP_INTEL`) | NEW | §10.5, §6.3 | X-02 / 8c→11 |
| 3 | **"Going cold" signal** — email-silence detection flags stalling targets/deals to analyst + partner | NEW | §10.5, §10.6 | A-03 / 14 |
| 4 | **First-class conversion funnel + stage conversion rates** on exec dashboard | ELEVATE | §10.6 | A-01 / 8c |
| 5 | **Scheduled report delivery** — auto-email status reports/digests on a cadence | NEW | §11.3, §8.6 | P-05+/14 |
| 6 | **Thesis monitor / continuous matching** — new pool entrants auto-matched & tagged to active theses | NEW | §7, §6.3 | S-07+/11 |
| 7 | **Signals-based ranking** — design `RANK_CANDIDATES` for acquisition history / capital deployment / hiring / adjacency (mock uses available fields now) | REFRAME | §6.3, §7.6 | S-07 / 11 |
| 8 | **AI company/deal summary** (`COMPANY_SUMMARY`) — one-paragraph brief from fields + timeline + notes | NEW | §6.3, App. C | P-/11 |
| 9 | **Self-serve, zero-admin simplicity** as a design principle (wedge vs DealCloud) | PRINCIPLE | §3-#16 | — |
| 10 | **Audit log + SOC 2 roadmap** for the executive buyer | NEW | §16 | F-/16 |

> None of these change the phase count; they extend existing phases (8c, 11, 14) and are all **mock-friendly** (relationship strength, going-cold, conversion rates are derived from the event log we already own; AI items degrade to the heuristic/mock). The research **confirmed** the core bet — projects-first workspace, cadence engine, sourcing pool, type-aware views — and **sharpened** it around auto-capture and relationship intelligence.

**Sources:** [Affinity vs DealCloud](https://www.affinity.co/comparison/affinity-vs-dealcloud) · [4Degrees IB CRM guide](https://www.4degrees.ai/blog/investment-banking-crm-guide-the-complete-playbook-for-relationship-driven-dealmakers) · [MadeMarket adoption](https://www.mademarket.com/blog/how-to-increase-crm-adoption-at-your-investment-bank) · [Affinity adoption rates](https://www.affinity.co/blog/crm-adoption-rates) · [GrowthFactor M&A CRM guide](https://www.growthfactor.ai/resources/blog/m-a-deal-management-crm) · [InetSoft M&A dashboard KPIs](https://www.inetsoft.com/info/mergers-and-acquisitions-dashboard/) · [Affinity auto email/meeting capture](https://www.affinity.co/blog/best-crm-automatic-email-meeting-capture) · [EthosData AI value stack](https://www.ethosdata.com/blog/ai-in-ma-the-5-layer-value-stack-that-will-define-dealmaking-in-2026-2030/) · [PrivSource AI deal-sourcing 2026](https://www.privsource.com/posts/best-ai-tools-for-m-and-a-deal-sourcing-2026) · [Navatar PE/M&A sourcing 2026](https://www.navatargroup.com/blog/private-equity-and-ma-deal-sourcing/) · [Grata AI](https://grata.com/technology/ai) · [4Degrees deal sourcing guide](https://www.4degrees.ai/blog/mastering-the-art-of-deal-sourcing-a-comprehensive-guide-for-investment-professionals)

---

## Appendix A — PRD ID coverage

| ID | Feature | Phase |
|---|---|---|
| S-01 | Proprietary DB ingest (normalise/dedupe) | 9, 10 |
| S-02 | Public CSV import | 10 |
| S-03 | Search pool by mandate criteria | 9 |
| S-04 | Push candidates → Master List | 9 |
| S-05 | Enrichment on candidate cards | 11 |
| S-06 | Pluggable external sources (arch only) | 16 |
| S-07 | AI ranking/suggestions | 11 (mock) → 13 (real) |
| P-01 | Gmail/Outlook send + auto-log + inbox sync | 12 (send) → 13 (sync) |
| P-02 | Email templates w/ merge fields | 12 |
| P-03 | Reminders / daily digest | 14 |
| P-04 | Per-project activity timeline | 15 |
| P-05 | Export to Excel/PDF | 15 |
| P-06 | Spreadsheet-import onboarding wizard | 10 |
| — | Projects-first workspace + both dashboards (mockups) | 8 |
| — | Role-aware views (analyst cockpit / exec portfolio) | 8 |
| — | Buy/sell/cap-raise type-aware workspace | 8 |
| — | Board (kanban) lens | 16 |
| X-02 | Relationship intelligence panel + strength score (research §19) | 8c → 11 |
| A-03 | "Going cold" / email-silence detection (research §19) | 14 |
| A-01+ | Conversion funnel + stage conversion rates, first-class (research §19) | 8c |
| — | Scheduled report delivery (research §19) | 14 |
| — | Thesis monitor / continuous matching (research §19) | 11 |
| — | AI company brief `COMPANY_SUMMARY` (research §19) | 11 |
| — | Audit log + SOC 2 readiness (research §19) | 15/16 |

## Appendix B — canonical import dictionary (header → field)

`Company Name→company_name · HQ→hq · Type→type · Status→status · Rationale→rationale · Revenue (source)→revenue_source · Revenue (INR Cr)→revenue_inr_cr · Headcount→headcount · Website→website · LinkedIn→linkedin · Relevant Investments→relevant_investments · Bucket→bucket · Contact Name→contact.full_name · Designation→contact.designation · Email→contact.email · Phone→contact.phone · Initial email (date)→event INITIAL_EMAIL.occurred_on` — fuzzy-matched in step 2, analyst-overridable. Mirrors the live Master List / Contact List columns (PRD §6.1, §6.3) so existing trackers map in one click.

## Appendix C — AI job I/O shapes (provider-agnostic)

```
RANK_CANDIDATES  in:{thesis, candidates[], signals?} out:[{candidate_id, score:0-100, rationale, signals_used[]}]
ENRICH           in:{name, domain, known_fields}      out:{fields:{revenue_inr_cr, headcount, hq, website, sector}, confidence}
DRAFT_EMAIL      in:{company, contact, thesis, tone}  out:{subject, body_html, merge_fields_used[]}
THESIS_MATCH     in:{thesis, pool_subset}             out:[{candidate_id, score, why}]   # also runs on new pool entrants (monitor)
DEDUPE_ASSIST    in:{row, candidates[]}               out:{match_id|null, confidence}
COMPANY_SUMMARY  in:{company_fields, timeline, notes} out:{summary, key_points[]}
RELATIONSHIP_INTEL in:{company|contact, cross_mandate_history} out:{warm_paths[], strength:0-100, rationale}
```
Mock and real providers return identical shapes (§6.2) — the UI and persistence are provider-blind.

---

*End of expansion plan. Build one phase at a time; keep the MVP invariants (append-only outreach, fixed-anchor cadence, firm-scoping, soft-delete) sacred; ship every phase demoable with zero secrets.*
