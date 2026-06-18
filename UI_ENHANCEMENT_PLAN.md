# Project Upstream — UI/UX Enhancement Plan
### "Bloomberg Terminal × Linear" · Design Sprint · 2026-06-10

---

## 1. BRUTAL OBSERVATIONS: The Teardown

### What This Is Right Now
A canonical `create-next-app` output with shadcn/ui bolted on and zero design decisions made. Every single choice is the installer's default. This is not a critique of the engineering — the data model, API design, and TypeScript coverage are solid. The *visual design* has not been touched.

### Evidence of Default Everything

**Font — Geist Sans.**
Vercel's bundled font. Auto-injected by `create-next-app` since 2023. Every Next.js project on GitHub that has never been designed uses Geist Sans. It screams "I accepted the defaults and shipped." An MD at a bulge bracket firm who opens this sees a side project, not institutional software.

**Color palette — Pure white with gray.**
`--background: oklch(1 0 0)` is `#FFFFFF`. The login background `bg-muted/30` resolves to `rgba(0,0,0,0.015)` — barely tinted white that reads as a white room under a single fluorescent light. The sidebar is `oklch(0.985 0 0)` = off-white by 1.5%. Cards are also white. There is no depth, no atmosphere, no hierarchy created through surface layering.

**Chart tokens — Five shades of gray.**
`--chart-1` through `--chart-5` are literally `oklch(0.87 0 0)` → `oklch(0.269 0 0)`. The developer noticed this and hardcoded `"#22c55e"`, `"#3b82f6"`, `"#ef4444"` directly into the dashboard JSX to escape the gray trap. That is a symptom, not a fix. The chart bar fill is Tailwind `blue-500` (`#3b82f6`) — the single most overused color in frontend development.

**Login page — Centered card on white.**
`<div className="bg-muted/30 flex min-h-screen items-center justify-center p-4">` with a `max-w-sm` Card inside. A `size-10` black square with a TrendingUp icon. CardTitle "Project Upstream". CardDescription "Sign in to your firm's deal book." This is the shadcn authentication demo, verbatim. There is zero drama, zero brand presence, zero conversion engineering.

**Dashboard — Five identical white boxes.**
Five `<StatCard>` components. The number is `text-2xl font-semibold` in Geist Sans. The label is `text-sm text-muted-foreground`. There is no typographic tension. The KPI value "142" looks exactly like any other text on the page — same font, same weight class, same color temperature. The only personality in the entire dashboard is a conditional `border-red-200` on the overdue card.

**Sidebar — Participation trophy.**
Active state: `bg-sidebar-accent text-sidebar-accent-foreground` = a marginally darker gray. Zero animation. Footer reads "Project Upstream · MVP" — literally telling your user this is an MVP. The brand icon is a black square. There is no sidebar identity.

**Motion — None.**
Not a single `@keyframes`. Not a single `transition` beyond color hovers. The most dynamic element in the entire frontend is `hover:bg-sidebar-accent/60`. This is a static document that happens to have React in it.

**Typography scale — Flat.**
Almost every label is `text-sm`. CardTitle in the dashboard is `text-sm`. Page headers are `text-xl font-semibold`. Stat card values are `text-2xl`. There is a 2-step ladder where there should be a 5-step hierarchy. Nothing commands attention.

### The Core Problem
This feels like a Notion clone built by someone who had never used Notion. The domain — M&A deal sourcing, hundred-million-dollar transactions, IB analysts under deadline pressure — demands an interface that communicates authority, precision, and urgency. What exists communicates none of these. A partner at a firm looking at this dashboard feels like they're reading a Google Sheet.

---

## 2. THE VISION: "Bloomberg Terminal × Linear"

### Aesthetic Manifesto

**The feeling**: You open the app and feel like you've entered a war room. Dark, precise, focused. The screen glows amber where it wants your attention. Every data point has weight. The typography is editorial, not friendly. This is not a consumer app — it is an instrument.

**The aesthetic DNA**:
- **Bloomberg Terminal**: Dark-first, amber/gold as the sole accent, dense data, zero decoration. Trusted by people who move markets.
- **Linear**: Perfect motion choreography, commanding sidebar, type system that makes a todo list feel architectural. The product that proved B2B tools can be beautiful.
- **Raycast**: Glass surfaces over dark backgrounds, blur depth, crisp monospaced data.
- **Vercel Dashboard**: Grid-pattern backgrounds that create depth without distraction, data rendered with care.

**The target emotion: Confidence.** The user opens this, sees their pipeline numbers in sharp amber-accented cards, feels the weight of the data, and trusts that this system is as serious as the work they're doing.

**The one rule that governs everything**: Amber is the only warm color. Every CTA, every urgency signal, every active state. The user's eye is trained to find amber = action required.

---

## 3. END-TO-END ENHANCEMENT PLAN

### 3.1 Typography Override

Remove: `Geist`, `Geist_Mono` from `layout.tsx` and all font variable references.

**New font stack:**

| Role | Font | Weight Range | Use |
|------|------|-------------|-----|
| Brand / Display | **Cormorant** | 400–700 | Logo wordmark, page titles (h1), hero text |
| UI Body | **Outfit** | 300–700 | All UI text, labels, body copy, nav items |
| Data / Mono | **JetBrains Mono** | 400–600 | KPI numbers, percentages, dates, IDs |

**Why this exact pairing:**

*Cormorant* is a high-contrast display serif with extreme thin/thick stroke variation. It is used by luxury brands, legal publishers, and financial institutions. At 28px+ it is breathtaking. It communicates heritage and precision that no sans-serif can replicate. It is completely absent from 99% of SaaS products.

*Outfit* is a geometric humanist sans. It is warm where Inter is cold, structured where Bricolage Grotesque is loose. Not a single other M&A CRM on the market uses it. It will feel immediately distinctive.

*JetBrains Mono* for all numeric values creates a "data terminal" aesthetic. Every KPI, percentage, and timestamp feels precise and intentional. It also has superior tabular figures out of the box.

**Typography rules:**

```
h1 (Page titles):       Cormorant, 28px / 700, letter-spacing -0.5px, --foreground
h2 (Card titles):       Outfit, 11px / 600, UPPERCASE, letter-spacing 0.08em, --text-tertiary
KPI values:             JetBrains Mono, 32px / 600, tabular-nums, --foreground
Body (labels/rows):     Outfit, 14px / 400, --foreground
Secondary text:         Outfit, 13px / 400, --text-secondary
Meta / timestamps:      JetBrains Mono, 12px / 400, --text-tertiary
Nav items:              Outfit, 13px / 500, --text-secondary (inactive) / --foreground (active)
Buttons:                Outfit, 13px / 600, letter-spacing 0.02em
```

The key shift: card titles become **tactical labels** (small, uppercase, muted) not decorative headings. KPI numbers become **commanding anchors** (large, mono, full brightness). This creates real typographic tension for the first time.

---

### 3.2 Color & Theming — "Obsidian Amber"

**Design principle:** One dominant dark tone. One warm accent. Surgical use of color for status signals only. No decorative pastels. No gradients in components. Gradients only in backgrounds for atmosphere.

**Complete CSS token redefinition** (replace entire `globals.css` `:root` and `.dark`):

```css
/* DARK MODE — this app is dark-first */
:root {
  /* ─── Background depth system ──────────────────────────────── */
  --background:          oklch(0.09 0.006 265);  /* #0A0B0F — base canvas, cool near-black */
  --card:                oklch(0.12 0.007 265);  /* #111419 — card surfaces               */
  --popover:             oklch(0.15 0.007 265);  /* #181C23 — modals, dropdowns, tooltips  */
  --secondary:           oklch(0.14 0.006 265);  /* #141720 — secondary surface            */
  --muted:               oklch(0.13 0.005 265);  /* #12151D — muted surface                */

  /* ─── Borders — translucent, not gray ──────────────────────── */
  --border:              oklch(1 0 0 / 0.07);    /* rgba(white, 7%) — default              */
  --input:               oklch(1 0 0 / 0.09);    /* rgba(white, 9%) — input backgrounds    */
  --ring:                oklch(0.72 0.16 58 / 0.5); /* amber focus ring at 50%            */

  /* ─── Amber accent — the only warm color ───────────────────── */
  --primary:             oklch(0.72 0.16 58);    /* #CC8500 — deep amber, not neon         */
  --primary-foreground:  oklch(0.98 0.005 80);   /* warm off-white on amber                */

  /* ─── Text hierarchy ────────────────────────────────────────── */
  --foreground:          oklch(0.95 0.006 80);   /* #F3EDE3 — warm off-white, not pure     */
  --card-foreground:     oklch(0.95 0.006 80);
  --popover-foreground:  oklch(0.95 0.006 80);
  --secondary-foreground: oklch(0.80 0.006 265); /* mid-bright for secondary               */
  --muted-foreground:    oklch(0.52 0.012 265);  /* #6B7490 — labels, placeholders         */
  --accent:              oklch(0.72 0.16 58 / 0.12); /* amber at 12% — hover surfaces      */
  --accent-foreground:   oklch(0.95 0.006 80);

  /* ─── Semantic ──────────────────────────────────────────────── */
  --destructive:         oklch(0.62 0.22 25);    /* red                                    */

  /* ─── Chart colors — vivid, not gray ───────────────────────── */
  --chart-1:             oklch(0.72 0.16 58);    /* amber  — primary series                */
  --chart-2:             oklch(0.65 0.18 152);   /* emerald — responded                   */
  --chart-3:             oklch(0.65 0.18 270);   /* indigo  — interested                  */
  --chart-4:             oklch(0.65 0.15 310);   /* violet  — 4th series                  */
  --chart-5:             oklch(0.62 0.22 25);    /* red     — bounced/declined             */

  /* ─── Sidebar ───────────────────────────────────────────────── */
  --sidebar:                    oklch(0.10 0.006 265); /* slightly darker than main bg     */
  --sidebar-foreground:         oklch(0.95 0.006 80);
  --sidebar-primary:            oklch(0.72 0.16 58);   /* amber for active state           */
  --sidebar-primary-foreground: oklch(0.98 0.005 80);
  --sidebar-accent:             oklch(0.72 0.16 58 / 0.10); /* amber 10% for active bg    */
  --sidebar-accent-foreground:  oklch(0.95 0.006 80);
  --sidebar-border:             oklch(1 0 0 / 0.06);
  --sidebar-ring:               oklch(0.72 0.16 58);

  --radius: 0.5rem;
}
```

**Status badge color mapping** (update `status-badge.tsx`):

| Status | Background | Text | Tailwind equiv (dark) |
|--------|-----------|------|----------------------|
| NOT_CONTACTED | `oklch(0.25 0.01 265 / 0.6)` | `oklch(0.55 0.01 265)` | Dark slate |
| CONTACTED | `oklch(0.30 0.02 265 / 0.6)` | `oklch(0.65 0.02 265)` | Steel |
| RESPONDED | `oklch(0.20 0.10 152 / 0.6)` | `oklch(0.65 0.18 152)` | Emerald |
| INTERESTED | `oklch(0.20 0.12 270 / 0.6)` | `oklch(0.65 0.18 270)` | Indigo |
| DECLINED | `oklch(0.22 0.08 58 / 0.6)` | `oklch(0.72 0.16 58)` | Amber |
| BOUNCED | `oklch(0.22 0.12 25 / 0.6)` | `oklch(0.62 0.22 25)` | Red |

**Mandate type and schedule status use the same system** — no more flat gray pills.

---

### 3.3 Spatial & Background Depth

**Layer 1 — Global body atmosphere:**
```css
body {
  background-color: var(--background);
  background-image:
    radial-gradient(
      ellipse 100% 40% at 50% -5%,
      oklch(0.72 0.16 58 / 0.05) 0%,
      transparent 60%
    );
}
```
Invisible at first glance. Felt as warmth at the top of the viewport. Creates a visual ceiling that grounds the layout.

**Layer 2 — Login page full-screen atmosphere:**
```css
.login-bg {
  background-color: oklch(0.09 0.006 265);
  background-image:
    /* Amber center glow — draws eye to the card */
    radial-gradient(
      ellipse 55% 45% at 50% 52%,
      oklch(0.72 0.16 58 / 0.07) 0%,
      transparent 65%
    ),
    /* Dot grid — depth without decoration */
    radial-gradient(
      circle,
      oklch(1 0 0 / 0.08) 1px,
      transparent 1px
    );
  background-size: auto, 28px 28px;
  background-position: center, center;
}
```

**Layer 3 — Card surfaces** (shadcn Card override):
- Default: `background: var(--card)` + `border: 1px solid var(--border)` — dark surface, barely-there border
- Interactive (table row hover): `background: oklch(0.72 0.16 58 / 0.04)` — amber tint so faint it's a feeling, not a color
- Elevated (modals): `background: var(--popover)` + `box-shadow: 0 0 0 1px oklch(1 0 0 / 0.06), 0 24px 48px oklch(0 0 0 / 0.5)`

**Layer 4 — Glassmorphism login card:**
```css
.login-card {
  background: oklch(0.12 0.007 265 / 0.75);
  backdrop-filter: blur(24px) saturate(160%);
  border: 1px solid oklch(1 0 0 / 0.10);
  box-shadow:
    0 0 0 1px oklch(0.72 0.16 58 / 0.08),
    0 32px 64px oklch(0 0 0 / 0.45),
    0 8px 16px oklch(0 0 0 / 0.25),
    inset 0 1px 0 oklch(1 0 0 / 0.06);
}
```

**Layer 5 — Overdue stat card amber signature** (when `overdue > 0`):
```css
.stat-card-overdue {
  border-color: oklch(0.72 0.16 58 / 0.45);
  box-shadow:
    0 0 0 1px oklch(0.72 0.16 58 / 0.15),
    inset 0 1px 0 oklch(0.72 0.16 58 / 0.08);
}
```

**Sidebar active item treatment:**
```css
.nav-item-active {
  background: oklch(0.72 0.16 58 / 0.10);
  color: oklch(0.95 0.006 80);
  /* Left border indicator — 2px amber bar */
  border-left: 2px solid oklch(0.72 0.16 58);
  padding-left: calc(0.75rem - 2px); /* compensate for border */
  box-shadow: inset 4px 0 12px oklch(0.72 0.16 58 / 0.06);
}
```

**Topbar depth:**
```css
header.topbar {
  background: oklch(0.09 0.006 265);
  border-bottom: 1px solid oklch(1 0 0 / 0.07);
  /* Subtle bottom glow creates floating effect */
  box-shadow: 0 1px 0 oklch(0.72 0.16 58 / 0.06);
}
```

---

### 3.4 Motion Choreography

**The governing rule:** One orchestrated entrance animation per page. Micro-interactions on every interactive element. Zero motion for motion's sake.

**Animation 1 — Dashboard KPI strip staggered reveal:**
```css
@keyframes stat-enter {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stat-card {
  animation: stat-enter 0.45s cubic-bezier(0.16, 1, 0.3, 1) backwards;
}
```
Apply via React `style` prop on each StatCard:
```tsx
style={{ animationDelay: `${index * 65}ms` }}
```
Five cards fan in over 260ms total. Feels deliberate, not mechanical.

**Animation 2 — Login card entrance:**
```css
@keyframes card-enter {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.975);
    filter: blur(3px);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
    filter: blur(0);
  }
}
.login-card {
  animation: card-enter 0.55s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
```
The blur-in prevents the card from "popping" into existence. It materializes.

**Animation 3 — Primary button amber shimmer (hover):**
```css
@keyframes btn-shimmer {
  0%   { background-position: -200% center; }
  100% { background-position:  200% center; }
}

button[data-variant="default"]:hover {
  background: linear-gradient(
    105deg,
    oklch(0.72 0.16 58) 0%,
    oklch(0.80 0.16 58) 45%,
    oklch(0.72 0.16 58) 100%
  );
  background-size: 200% auto;
  animation: btn-shimmer 1.8s linear infinite;
}
```
Works purely in CSS. The amber button literally glows on hover — makes "Sign In" and "Log Outreach" impossible to miss.

**Animation 4 — Sidebar nav active indicator slide:**
```css
.nav-item {
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
  position: relative;
}

.nav-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 20%;
  height: 60%;
  width: 2px;
  background: var(--primary);
  border-radius: 0 2px 2px 0;
  transform: scaleY(0);
  transform-origin: center;
  transition: transform 0.22s cubic-bezier(0.16, 1, 0.3, 1);
}

.nav-item.active::before {
  transform: scaleY(1);
}
```
The amber indicator slides in from center. Not a pop, a reveal.

**Animation 5 — Overdue card pulse (when overdue > 0):**
```css
@keyframes amber-pulse {
  0%, 100% {
    box-shadow:
      0 0 0 1px oklch(0.72 0.16 58 / 0.30),
      inset 0 1px 0 oklch(0.72 0.16 58 / 0.08);
  }
  50% {
    box-shadow:
      0 0 0 2px oklch(0.72 0.16 58 / 0.15),
      0 0 24px oklch(0.72 0.16 58 / 0.10),
      inset 0 1px 0 oklch(0.72 0.16 58 / 0.08);
  }
}
.stat-card-overdue-active {
  animation: amber-pulse 2.5s ease-in-out infinite;
}
```
Gentle. Not a strobe. A heartbeat. Urgency without panic.

**Animation 6 — Table row stagger on load:**
```css
@keyframes row-enter {
  from { opacity: 0; transform: translateX(-6px); }
  to   { opacity: 1; transform: translateX(0); }
}

.data-row {
  animation: row-enter 0.25s cubic-bezier(0.16, 1, 0.3, 1) backwards;
  animation-delay: calc(var(--row-i, 0) * 25ms);
}
```
Apply `style={{ '--row-i': index } as React.CSSProperties}` on each `<tr>`.

**Animation 7 — KPI count-up numbers:**
Create `hooks/use-counter.ts`:
```ts
export function useCounter(target: number, duration = 800) {
  const [value, setValue] = useState(0);
  useEffect(() => {
    if (!target) return;
    const start = performance.now();
    const tick = (now: number) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
      setValue(Math.round(eased * target));
      if (progress < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }, [target, duration]);
  return value;
}
```
Use in StatCard when value is a number. The numbers tick up on page load — a financial terminal staple.

**Reduced motion compliance:**
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 4. CONVERSION ARCHITECTURE

### The Attention Funnel

In this CRM, "conversion" is the user taking action on their pipeline — logging outreach, creating mandates, addressing overdue items. Every design decision either accelerates or slows this.

**Step 1 — Eye entry point: Amber KPI numbers.**
When the dashboard loads and the stat cards stagger in, the eye is immediately drawn to the largest text on the screen. That text is in JetBrains Mono at 32px, in the warmest color on the page. Numbers are the message. The user immediately knows: "142 companies, 23% responded, 8 overdue."

**Step 2 — Urgency signal: Overdue amber pulse.**
The pulsing amber border on the overdue card is the only animated element on the dashboard. Animation = priority. The user's eye finds it even if they're not looking for it. This directly drives them to the schedule page.

**Step 3 — Primary action discoverability: Single amber CTA.**
On every page, there is exactly one amber element at full opacity: the primary action button. On the login page it is "Sign In." On the schedule page it is "Log Outreach." On the companies page it is "Add Company." On mandate detail it is "Add Company to Mandate." Amber = do this now. Everything else is dark.

**Step 4 — Navigation authority: Active amber indicator.**
The sidebar amber left-border for the active route anchors the user spatially. They always know where they are. Linear's sidebar is the gold standard for this — this implementation mirrors it directly.

**Step 5 — Data row hover: Amber tint CTA surface.**
Table rows get `background: oklch(0.72 0.16 58 / 0.04)` on hover — imperceptible unless you're looking, but it creates a micro-affordance that the row is clickable. The cursor changes to pointer simultaneously.

### Login Page Specific Conversion

The current login page fails to communicate **why this product matters** before the user even types their credentials. Replace:

- *Current*: "Sign in to your firm's deal book"
- *New*: "Deal intelligence, institutionalized."

The brand mark "Upstream" in Cormorant at 48px above the card establishes authority before the card even loads. The user doesn't need the card to trust the product — the typography does it first.

The amber Sign In button, with its shimmer hover state, is the visual destination the user's eye is led to by the entire composition. White grid → amber center glow → dark glass card → amber button. A straight line.

### Schedule Page Hierarchy

The schedule page has four sections: Needs first outreach, Overdue, Due today, Due this week. Current implementation treats all four equally. New hierarchy:

1. **Overdue section**: Amber-tinted card background (`oklch(0.72 0.16 58 / 0.05)`) + amber section header + red count badge. First thing you see.
2. **Due today**: Slightly elevated surface. White section header. Normal priority.
3. **Due this week**: Default surface. Muted header.
4. **Needs first outreach**: Separate card below the fold. Informational, not urgent.

The user who has 3 overdue items cannot miss them. The visual hierarchy creates emotional urgency that matches the business urgency.

---

## 5. EXECUTION ROADMAP

### Phase 1 — Foundation: Tokens & Typography `~2.5h`

- [ ] **1.1** Update `layout.tsx`: remove `Geist`/`Geist_Mono`, add `Cormorant`, `Outfit`, `JetBrains_Mono` via `next/font/google`
- [ ] **1.2** Update `@theme inline` block in `globals.css`: wire `--font-display` (Cormorant), `--font-sans` (Outfit), `--font-mono` (JetBrains Mono)
- [ ] **1.3** Replace entire `:root` block with Obsidian Amber token set from §3.2
- [ ] **1.4** Remove `.dark` block (app is now dark-first; retain only for optional light mode later)
- [ ] **1.5** Add `class="dark"` to `<html>` in `layout.tsx` (force dark mode)
- [ ] **1.6** Add global body radial gradient to `globals.css` (§3.3 Layer 1)
- [ ] **1.7** Add all 7 keyframe animation blocks to `globals.css`
- [ ] **1.8** Add `prefers-reduced-motion` block
- [ ] **1.9** Smoke-test: run `npm run dev`, verify dark background loads, Outfit font visible

### Phase 2 — Login Page Transformation `~1.5h`

- [ ] **2.1** Wrap root div in `login-bg` class: dark bg + dot grid + amber center glow (§3.3 Layer 2)
- [ ] **2.2** Add above-card brand block: `<h1>` in Cormorant 48px + tagline "Deal intelligence, institutionalized."
- [ ] **2.3** Replace shadcn `Card` with a plain `div` applying glassmorphism styles (§3.3 Layer 4) — keep all form logic unchanged
- [ ] **2.4** Apply `card-enter` animation class to login card div
- [ ] **2.5** Add amber focus ring to `Input` components: `focus:border-primary/50 focus:ring-primary/30`
- [ ] **2.6** Verify Sign In button renders amber (it uses `variant="default"` which maps to `--primary`)
- [ ] **2.7** Update CardDescription copy → "Deal intelligence, institutionalized." (or remove if above-card tagline is used)
- [ ] **2.8** Remove TrendingUp black square — the Cormorant wordmark IS the brand mark at this scale

### Phase 3 — Sidebar Identity `~1h`

- [ ] **3.1** Update brand area: "Upstream" in `font-display` (Cormorant), 18px, font-weight 600
- [ ] **3.2** Apply `::before` pseudo-element for animated amber left-border active indicator (§3.4 Animation 4) — note: this requires replacing the Link with a wrapper div+Link or using a Tailwind `before:` approach
- [ ] **3.3** Active state: replace `bg-sidebar-accent` with `bg-primary/10 border-l-2 border-primary`
- [ ] **3.4** Inactive nav item color: `text-muted-foreground` → lower opacity, hover brings to `text-foreground`
- [ ] **3.5** Footer: replace "Project Upstream · MVP" with user's firm name from auth context (already available via `useAuth()`)
- [ ] **3.6** Sidebar background: verify `--sidebar` token resolves to slightly darker than `--background`

### Phase 4 — Dashboard Overhaul `~2.5h`

- [ ] **4.1** PageHeader title: apply `font-display` class (Cormorant), increase to `text-3xl`
- [ ] **4.2** Add greeting: "Good morning, [first name]" subheading in Outfit 14px muted
- [ ] **4.3** StatCard value: change `text-2xl font-semibold` → `text-3xl font-semibold font-mono` (JetBrains Mono via CSS class)
- [ ] **4.4** StatCard label: change to uppercase + tracking-wider + 11px + muted (tactical label style)
- [ ] **4.5** Add `style={{ animationDelay: ... }}` prop to each StatCard in dashboard (§3.4 Animation 1) — pass `index` from `.map()`
- [ ] **4.6** Overdue StatCard: add conditional `stat-card-overdue-active` class when `overview?.overdue > 0` (amber pulse, §3.4 Animation 5)
- [ ] **4.7** Charts — Status donut: replace `STATUS_COLORS` with CSS variable references matching new chart tokens
- [ ] **4.8** Charts — Bar chart: replace `fill="#3b82f6"` with `fill="var(--chart-1)"` (amber), update Tooltip `contentStyle` for dark background
- [ ] **4.9** Chart card title: apply tactical label style (uppercase, tracking, muted, Outfit 11px)
- [ ] **4.10** Recharts tick color: pass `style={{ fill: 'var(--muted-foreground)' }}` to XAxis/YAxis `tick` props
- [ ] **4.11** Due this week list: add `hover:bg-primary/[0.04]` to list items

### Phase 5 — Component System Polish `~2h`

- [ ] **5.1** `status-badge.tsx`: update all 6 status colors to dark-mode table from §3.2; update `CadenceBadge` similarly
- [ ] **5.2** `button.tsx` variant `default`: verify amber background renders (should come from `--primary` token already)
- [ ] **5.3** `button.tsx` variant `outline`: dark border `border-border`, dark bg `bg-transparent`, hover `bg-accent`
- [ ] **5.4** `data-table.tsx`: add `style={{ '--row-i': index } as React.CSSProperties}` and `data-row` class to each `<tr>`; apply `row-enter` animation
- [ ] **5.5** `data-table.tsx` header: `bg-muted/50` → `bg-card` with uppercase Outfit 11px tracking label style on `<th>`
- [ ] **5.6** `stat-card.tsx`: apply `font-mono tabular-nums` to value div; apply `text-[11px] uppercase tracking-widest` to label
- [ ] **5.7** `page-header.tsx`: title → `font-display text-3xl font-semibold`
- [ ] **5.8** `topbar.tsx`: apply topbar depth styles from §3.3; verify dark background
- [ ] **5.9** `empty-state.tsx`: icon color → `text-primary/40` (amber, faded)

### Phase 6 — Supporting Pages `~2h`

- [ ] **6.1** `/companies`: update `source` dot color → amber for PROPRIETARY, keep others semantic
- [ ] **6.2** `/schedule`: add overdue section amber background treatment; reorder sections (Overdue first)
- [ ] **6.3** `/analytics`: update all chart fills to use `--chart-1` through `--chart-5` tokens; table headers get tactical label style
- [ ] **6.4** `/companies/[id]` tabs: active tab underline → amber (`border-b-2 border-primary`)
- [ ] **6.5** All dialogs: verify `bg-popover` resolves to `--popover` token (elevated dark surface); add `card-enter` animation to dialog content
- [ ] **6.6** `/mandates`: type and status badges update to new color system
- [ ] **6.7** `error.tsx` / `not-found.tsx`: dark background, Cormorant error heading

### Phase 7 — Motion Layer `~1.5h`

- [ ] **7.1** Create `hooks/use-counter.ts` (count-up animation, §3.4 Animation 7)
- [ ] **7.2** Update `StatCard` to use `useCounter` when value is a number (pass raw number, display formatted)
- [ ] **7.3** Verify shimmer on `button[data-variant="default"]:hover` — check that shadcn Button renders `data-variant` attribute (if not, use `.bg-primary:hover` selector or add explicit class)
- [ ] **7.4** Verify all CSS animations have `backwards` fill-mode where appropriate (prevents flash on load)
- [ ] **7.5** Test `prefers-reduced-motion` in browser DevTools — confirm all animations freeze

### Phase 8 — Verification & QA `~1h`

- [ ] **8.1** Contrast audit: check `--foreground` on `--background`, `--foreground` on `--card`, amber on `--background` all pass WCAG AA (4.5:1 for text, 3:1 for UI)
- [ ] **8.2** Check every page: login, dashboard, companies, company-detail, schedule, contacts, mandates, mandate-detail, analytics, settings
- [ ] **8.3** Mobile: sidebar hidden at < md, stat cards in 2-col, topbar firm name truncates
- [ ] **8.4** `grep -r "Geist"` in `frontend/` — should return zero results
- [ ] **8.5** `grep -r "#3b82f6\|#22c55e\|#ef4444\|#f59e0b"` — all hardcoded hex colors replaced with tokens
- [ ] **8.6** `npm run build` — zero TypeScript errors
- [ ] **8.7** Side-by-side screenshot: login, dashboard before vs. after

---

## Appendix A — Font Loading Code (`layout.tsx`)

```typescript
import { Cormorant, Outfit, JetBrains_Mono } from "next/font/google";

const cormorant = Cormorant({
  variable: "--font-display",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  display: "swap",
});

const outfit = Outfit({
  variable: "--font-sans",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  display: "swap",
});

// In RootLayout:
<html
  lang="en"
  className={`${cormorant.variable} ${outfit.variable} ${jetbrainsMono.variable} dark h-full antialiased`}
>
```

## Appendix B — Before / After Contract

| Element | Before | After |
|---------|--------|-------|
| Background | `#FFFFFF` (pure white) | `oklch(0.09 0.006 265)` ≈ `#0A0B0F` |
| Body font | Geist Sans (Vercel default) | Outfit (geometric humanist) |
| Brand/heading font | Geist Sans | Cormorant (high-contrast serif) |
| Number/data font | Geist Sans | JetBrains Mono |
| CTA button color | `oklch(0.205 0 0)` (charcoal) | `oklch(0.72 0.16 58)` (amber) |
| Active nav state | Slightly darker gray bg | Amber left-border + amber glow bg |
| Chart bars | `#3b82f6` (Tailwind blue-500) | `var(--chart-1)` (amber) |
| Chart tokens | 5 shades of gray | Amber / Emerald / Indigo / Violet / Red |
| Login background | `bg-muted/30` (barely-white) | Dark + dot grid + amber center glow |
| Login card | Flat white shadcn Card | Glassmorphism dark panel |
| Card background | `#FFFFFF` | `oklch(0.12 0.007 265)` ≈ `#111419` |
| Card border | `oklch(0.922 0 0)` (gray) | `oklch(1 0 0 / 0.07)` (translucent white) |
| Stat card KPI value | `text-2xl font-semibold` Geist | `text-3xl font-mono` JetBrains Mono |
| Stat card label | `text-sm text-muted-foreground` | 11px uppercase tracking-widest muted |
| Motion | None | Staggered entrance + shimmer + pulse + count-up |
| Sidebar footer | "Project Upstream · MVP" | Firm name from auth context |
| Status badges | Flat color pills | Dark-bg translucent pills, vivid text |

## Appendix C — Amber Reference Values

| Purpose | OKLCH | Approx Hex |
|---------|-------|-----------|
| Full accent | `oklch(0.72 0.16 58)` | `#C47D08` |
| Hover/lighter | `oklch(0.78 0.16 58)` | `#D48E0F` |
| Active bg (10%) | `oklch(0.72 0.16 58 / 0.10)` | `rgba(196,125,8,0.10)` |
| Glow (5%) | `oklch(0.72 0.16 58 / 0.05)` | `rgba(196,125,8,0.05)` |
| Border (40%) | `oklch(0.72 0.16 58 / 0.40)` | `rgba(196,125,8,0.40)` |
| Focus ring (50%) | `oklch(0.72 0.16 58 / 0.50)` | `rgba(196,125,8,0.50)` |
