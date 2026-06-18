# Project Upstream — What We're Building Next

### A plain-language feature overview for the team

*Prepared for project management / non-technical stakeholders · June 2026*

---

## The big picture in one paragraph

Project Upstream is the software that replaces the messy stack of **Excel sheets, inboxes, and manual trackers** that boutique M&A firms use to run their deal outreach. The **core engine is already built and working** — it tracks every target company, every email, and automatically tells analysts who to follow up with and when. This document covers the **next chapter**: turning that engine into a polished, deal-by-deal workspace, pulling in the firm's real data automatically, and adding smart assistance — so the product is faster than a spreadsheet for the analyst and gives partners total visibility for the first time.

---

## Who uses it (and why they care)

The product serves **two very different people**, and a lot of our design effort goes into serving both well:

| | **The Analyst** (does the daily work) | **The Partner / MD** (runs the firm) |
|---|---|---|
| **Their job** | Build target lists, send outreach, never miss a follow-up | Oversee all deals, win mandates, protect the firm's reputation |
| **What they want** | Speed, less typing, "what do I do today?" | "Are all our deals healthy? Is anyone behind? No embarrassing mistakes." |
| **We give them** | A fast, focused workspace per deal | A bird's-eye dashboard across every deal |

> **Key insight from our market research:** the people who *use* the tool every day and the people who *pay* for it are different — so we're deliberately giving each their own view of the same information.

---

## What's already working today (the foundation)

So everyone knows the starting point — these are **done and tested**:

- ✅ Each firm has its own private, secure space; analysts only see the deals they're assigned to.
- ✅ A central list of all target/buyer companies per deal.
- ✅ **Automatic follow-up scheduling** — the system knows when each company is due for its next email and flags anything overdue.
- ✅ A complete, permanent history of every email and touch (nothing ever gets overwritten or lost).
- ✅ A contact database that survives staff turnover.
- ✅ Duplicate detection so two analysts don't embarrassingly email the same target.
- ✅ Basic dashboards and analytics.

The next chapter builds **on top of** this — it doesn't replace any of it.

---

## What we're building next — by theme

### 1. A workspace organized around each deal ("Projects")
Today everything is in one big list. We're reorganizing it so **each deal is its own "Project"** with its own page, its own dashboard, and a quick switcher to jump between them — exactly like the mockups we've shared. Analysts will also be able to **create their own projects** (today only partners can).

**Why it matters:** analysts think one deal at a time. This matches how they actually work and makes the tool feel purpose-built, not generic.

### 2. The analyst "cockpit" — getting through the day fast
Inside each project, the analyst gets a **focused command center**: a prioritized to-do list (overdue first, then due today, then this week) on the left, and a detail panel on the right where they can log an email, schedule one, or mark a response **without ever losing their place**. They can flip between this list view, a pipeline board, and a spreadsheet-style grid depending on preference.

It also **adapts to the type of deal**: on a *sell-side* deal it talks about "Buyers," on a *buy-side* deal it talks about "Targets," on a fundraise it talks about "Investors" — same screen, right language.

**Why it matters:** this is the feature that makes us **faster than a spreadsheet**. If it's not faster, analysts won't switch.

### 3. The executive view — total visibility, no surprises
Partners get a **firm-wide dashboard**: every deal's health at a glance, who's behind on follow-ups, a conversion funnel (how many contacted → responded → interested), and alerts for any **duplicate outreach** or **deals going quiet**. They can drill into any deal to see exactly what's happening.

**Why it matters:** this is what the *buyer* pays for — confidence that nothing is slipping and the firm's reputation is protected.

### 4. Bringing in your real data — automatically
Two ways the platform fills itself with real information instead of manual typing:
- **Excel/CSV import wizard** — upload your existing spreadsheets and a guided flow maps the columns, removes duplicates, and loads everything in minutes. Fully reversible if something looks wrong.
- **Email sync** — connect your Gmail or Outlook (sign in with your Google or company account) and the platform **automatically records** outreach you send, even from your own inbox.

**Why it matters:** our research found the **#1 reason firms abandon these tools is the burden of manual data entry.** Removing it is the difference between a tool people use and one they quietly drop.

### 5. Email & follow-ups, handled by the platform
Analysts can **write and send outreach directly from the platform** (or schedule it to go out later), and it gets logged automatically. If a partner emails a target from their own inbox, the platform **notices and logs it for the deal on the analyst's behalf** — so the tracker stays accurate without anyone doing extra work. Reusable **email templates** with auto-filled company/contact details make this fast.

**Why it matters:** this is the single biggest time-saver and the feature that keeps people in the tool every day.

### 6. Finding new targets ("Sourcing")
A searchable pool of candidate companies the firm can filter by sector, geography, size, and type — then **push the best ones into a deal with one click** (which automatically starts the follow-up schedule). The firm can load its own proprietary database and public-source lists into this pool.

**Why it matters:** it closes the loop — *find a target → reach out → track it → remember it* — all in one place.

### 7. Smart assistance (AI)
AI features that **accelerate** the analyst rather than replace their judgment: ranking candidate companies by fit to the deal, filling in missing company details, drafting outreach emails, summarizing a company's history in a paragraph, and surfacing **who at the firm already knows a target** (warm introductions). Everything the AI suggests is reviewed and approved by a human — it never acts on its own.

> **Important for budgeting:** we're building all of this to **work with sample data today, with no AI subscription required.** When you're ready to turn on the "real" AI, it's a simple settings change — no rebuild. The same applies to the email integrations. *This lets us build and demo the entire product now, and only start paying for outside services when you choose to.*

### 8. Staying on top of things
- **Daily reminder digest** emailed to each analyst: what's due, what's overdue, who responded.
- **"Going cold" alerts** when a promising target has gone quiet too long.
- **Scheduled reports** auto-emailed to partners (clean status reports for clients).
- **Export to Excel/PDF** for client updates.
- **Activity timeline** per deal — a full record of who did what, useful for oversight and audit.

---

## Why these features (not others) — the research

We checked our plan against how the market's leading tools (Affinity, DealCloud, and others) win and lose. Three things stood out and shaped the plan:

1. **Manual data entry kills these tools.** The top reason firms abandon a CRM is the typing burden. → We made **automatic email capture the centerpiece**, not an afterthought.
2. **Relationship intelligence wins mandates.** Knowing "who already knows this target" is a top analyst request. → We're surfacing the firm's shared history as **warm-introduction paths**.
3. **The big incumbents are slow and heavy** — they take months to set up and need dedicated admins. → Our edge is **being live in minutes** with the import wizard and **needing no admin**. That's our way in with small firms.

---

## Rough build sequence

These are grouped into stages we can demo as we go. Estimates are **build effort**, not calendar time, and assume the current pace.

| Stage | What you'll be able to show | Rough effort |
|---|---|---|
| **1. The deal workspace** | The Projects screen, per-deal dashboards, the analyst cockpit, the executive view (your mockups, live) | ~1 week |
| **2. Real data in** | Excel import wizard + the sourcing pool of candidate companies | ~1.5 weeks |
| **3. Smart assistance** | AI ranking, enrichment, email drafting, company briefs (on sample data) | ~1 week |
| **4. Email on autopilot** | Send/schedule from the platform + auto-logging + Google/Microsoft sign-in + inbox sync | ~1.5 weeks |
| **5. Stay on top** | Reminders, "going cold" alerts, scheduled reports, templates, exports, activity log | ~1.5 weeks |

> **Recommended starting point: Stage 1**, because it puts the screens from our mockups in front of people immediately and is the most visible proof of progress.

A nice property of this order: **Stages 1–3 work entirely on sample data with no outside subscriptions** — so we can build, demo, and gather feedback before spending a rupee on AI or email services. Real keys only matter at Stage 4, and even then the rest keeps working without them.

---

## What we'd like decided

A couple of small calls that affect the build (happy to recommend defaults):
1. **Naming** — do we call them "Projects" everywhere, or keep "Mandate" in partner-facing areas (the formal industry term)?
2. **Associates** — should associates get the analyst (hands-on) view or the partner (oversight) view by default?

---

*This is the business-friendly summary. The full technical specification — data design, build phases, and acceptance criteria — lives in `EXPANSION_PLAN.md` for the engineering team.*
