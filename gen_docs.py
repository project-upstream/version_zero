"""Generate Project Upstream User Guide PDF."""

from fpdf import FPDF
from fpdf.enums import XPos, YPos

NAV  = (15,  23,  42)
GOLD = (180, 120,   8)
GRN  = (34,  197,  94)
RED  = (220,  38,  38)
WHT  = (255, 255, 255)
LGRY = (248, 250, 252)
MGRY = (226, 232, 240)
DGRY = (100, 116, 139)
BODY = (30,   41,  59)
INDG = (99,  102, 241)


class Doc(FPDF):
    L = 18
    R = 192
    W = 174

    def header(self):
        if self.page_no() == 1:
            return
        self.set_fill_color(*NAV)
        self.rect(0, 0, 210, 11, "F")
        self.set_fill_color(*GOLD)
        self.rect(0, 11, 210, 0.8, "F")
        self.set_font("Helvetica", "B", 7.5)
        self.set_text_color(*LGRY)
        self.set_xy(self.L, 3)
        self.cell(0, 5, "PROJECT UPSTREAM  |  User Guide", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*BODY)
        self.ln(5)

    def footer(self):
        self.set_y(-11)
        self.set_draw_color(*MGRY)
        self.set_line_width(0.3)
        self.line(self.L, self.get_y(), self.R, self.get_y())
        self.ln(1.5)
        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(*DGRY)
        self.cell(0, 4, "Page " + str(self.page_no()), align="C")

    def h1(self, num, txt):
        self.set_fill_color(*NAV)
        self.set_x(0)
        self.cell(210, 14, "", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_y(self.get_y() - 14)
        self.set_x(self.L)
        self.set_font("Helvetica", "B", 7)
        self.set_text_color(*GOLD)
        self.cell(self.W, 4.5, num, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_x(self.L)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*WHT)
        self.cell(self.W, 8, txt, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*BODY)
        self.ln(5)

    def h2(self, txt):
        self.ln(4)
        self.set_font("Helvetica", "B", 10.5)
        self.set_text_color(*NAV)
        self.set_x(self.L)
        self.cell(self.W, 6, txt, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*GOLD)
        self.set_line_width(0.4)
        self.line(self.L, self.get_y(), self.R, self.get_y())
        self.ln(3)
        self.set_text_color(*BODY)

    def h3(self, txt):
        self.ln(2)
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(*GOLD)
        self.set_x(self.L)
        self.cell(self.W, 5.5, txt, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*BODY)
        self.ln(0.5)

    def para(self, txt):
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*BODY)
        self.set_x(self.L)
        self.multi_cell(self.W, 5.5, txt)
        self.ln(1.5)

    def bullet(self, items):
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*BODY)
        for item in items:
            self.set_x(self.L + 5)
            self.cell(5, 5.5, "-")
            self.set_x(self.L + 10)
            self.multi_cell(self.W - 10, 5.5, item)
        self.ln(1)

    def callout(self, txt):
        x, y = self.L, self.get_y()
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*BODY)
        self.set_fill_color(255, 251, 235)
        self.set_x(x + 3)
        self.multi_cell(self.W - 6, 5, txt, fill=True)
        h = self.get_y() - y
        self.set_draw_color(*GOLD)
        self.set_line_width(0.35)
        self.rect(x, y, self.W, h + 1.5, "D")
        self.set_fill_color(*GOLD)
        self.rect(x, y, 2.5, h + 1.5, "F")
        self.ln(3)

    def kv(self, label, value):
        self.set_x(self.L)
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(*DGRY)
        self.cell(42, 5.5, label)
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*BODY)
        self.multi_cell(self.W - 42, 5.5, value)

    def perm_table(self, headers, rows):
        cw = [self.W - 36, 18, 18]
        self.set_fill_color(*NAV)
        self.set_text_color(*WHT)
        self.set_font("Helvetica", "B", 8)
        self.set_x(self.L)
        for i, h in enumerate(headers):
            self.cell(cw[i], 6.5, h, border=0, fill=True, align="C" if i > 0 else "L")
        self.ln()
        for r, row in enumerate(rows):
            bg = LGRY if r % 2 == 0 else WHT
            self.set_fill_color(*bg)
            self.set_x(self.L)
            self.set_font("Helvetica", "", 8.5)
            self.set_text_color(*BODY)
            self.cell(cw[0], 6, row[0], border=0, fill=True)
            for i, v in enumerate(row[1:], 1):
                self.set_font("Helvetica", "B", 9)
                self.set_text_color(*(GRN if v == "Y" else (RED if v == "N" else DGRY)))
                self.cell(cw[i], 6, v, border=0, fill=True, align="C")
            self.set_text_color(*BODY)
            self.ln()
        self.ln(3)

    def event_table(self, headers, rows):
        cw = [self.W - 44, 22, 22]
        self.set_fill_color(*NAV)
        self.set_text_color(*WHT)
        self.set_font("Helvetica", "B", 8)
        self.set_x(self.L)
        for i, h in enumerate(headers):
            self.cell(cw[i], 6.5, h, border=0, fill=True)
        self.ln()
        for r, row in enumerate(rows):
            bg = LGRY if r % 2 == 0 else WHT
            self.set_fill_color(*bg)
            self.set_x(self.L)
            self.set_font("Helvetica", "", 8.5)
            self.set_text_color(*BODY)
            self.multi_cell(cw[0], 5.5, row[0], fill=True)
            cur_y = self.get_y()
            self.set_xy(self.L + cw[0], cur_y - 5.5)
            for i, v in enumerate(row[1:], 1):
                self.set_font("Helvetica", "", 8)
                self.set_text_color(*DGRY)
                self.cell(cw[i], 5.5, v, border=0, fill=True)
            self.ln()
        self.ln(3)

    def cred_table(self, headers, rows):
        cw = [self.W - 46, 24, 22]
        self.set_fill_color(*NAV)
        self.set_text_color(*WHT)
        self.set_font("Helvetica", "B", 8)
        self.set_x(self.L)
        for i, h in enumerate(headers):
            self.cell(cw[i], 6.5, h, border=0, fill=True)
        self.ln()
        for r, row in enumerate(rows):
            bg = LGRY if r % 2 == 0 else WHT
            self.set_fill_color(*bg)
            self.set_x(self.L)
            for i, v in enumerate(row):
                self.set_font("Helvetica", "B" if i == 1 else "", 8.5)
                self.set_text_color(*(INDG if i == 1 else BODY))
                self.cell(cw[i], 6, v, border=0, fill=True)
            self.ln()
        self.ln(3)

    def status_badge(self, label, colour, desc):
        y = self.get_y() + 1
        self.set_fill_color(*colour)
        self.rect(self.L, y, 28, 5, "F")
        self.set_font("Helvetica", "B", 7)
        self.set_text_color(*WHT)
        self.set_xy(self.L, y)
        self.cell(28, 5, label, align="C")
        self.set_x(self.L + 31)
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*BODY)
        self.multi_cell(self.W - 31, 5.5, desc)
        self.ln(1)

    def step(self, n, title, detail):
        x, y = self.L, self.get_y()
        self.set_fill_color(*GOLD)
        self.ellipse(x, y, 6.5, 6.5, "F")
        self.set_font("Helvetica", "B", 8.5)
        self.set_text_color(*WHT)
        self.set_xy(x, y)
        self.cell(6.5, 6.5, str(n), align="C")
        self.set_xy(x + 9, y)
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(*NAV)
        self.cell(60, 5, title)
        self.ln(5)
        self.set_x(x + 9)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*DGRY)
        self.multi_cell(self.W - 9, 4.8, detail)
        self.ln(2)

    def two_col(self, label, desc, lw=36):
        self.set_x(self.L)
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(*NAV)
        self.cell(lw, 5.5, label)
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*BODY)
        self.multi_cell(self.W - lw, 5.5, desc)

    def role_block(self, role, subtitle, colour, body_txt):
        y = self.get_y()
        self.set_fill_color(22, 37, 66)
        self.set_x(self.L)
        # measure height: rough estimate then draw
        self.set_font("Helvetica", "", 9)
        lines = len(body_txt) // 90 + 3
        bh = 13 + lines * 5
        self.rect(self.L, y, self.W, bh, "F")
        self.set_fill_color(*colour)
        self.rect(self.L, y, 3, bh, "F")
        self.set_xy(self.L + 7, y + 2)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*[min(255, int(c * 1.3)) for c in colour])
        self.cell(self.W - 7, 6, role)
        self.ln(6)
        self.set_x(self.L + 7)
        self.set_font("Helvetica", "I", 8.5)
        self.set_text_color(148, 163, 184)
        self.cell(self.W - 7, 5, subtitle)
        self.ln(5.5)
        self.set_x(self.L + 7)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(203, 213, 225)
        self.multi_cell(self.W - 10, 5, body_txt)
        self.set_text_color(*BODY)
        self.ln(4)


# ============================================================================
pdf = Doc(orientation="P", unit="mm", format="A4")
pdf.set_auto_page_break(auto=True, margin=15)
pdf.set_margins(18, 15, 18)


# ── COVER ────────────────────────────────────────────────────────────────────
pdf.add_page()

pdf.set_fill_color(*NAV)
pdf.rect(0, 0, 210, 120, "F")
pdf.set_fill_color(*GOLD)
pdf.rect(0, 120, 210, 2.5, "F")
pdf.set_fill_color(22, 37, 66)
pdf.rect(0, 122.5, 210, 80, "F")

pdf.set_fill_color(*GOLD)
pdf.rect(18, 26, 22, 22, "F")
pdf.set_font("Helvetica", "B", 14)
pdf.set_text_color(*NAV)
pdf.set_xy(18, 30)
pdf.cell(22, 14, "PU", align="C")

pdf.set_font("Helvetica", "B", 28)
pdf.set_text_color(*WHT)
pdf.set_xy(46, 26)
pdf.cell(140, 13, "Project Upstream")
pdf.set_xy(46, 40)
pdf.set_font("Helvetica", "", 12)
pdf.set_text_color(148, 163, 184)
pdf.cell(140, 7, "M&A Deal-Sourcing CRM")

pdf.set_xy(18, 72)
pdf.set_font("Helvetica", "B", 18)
pdf.set_text_color(*WHT)
pdf.cell(174, 10, "User Guide", align="L")
pdf.set_xy(18, 83)
pdf.set_font("Helvetica", "", 9.5)
pdf.set_text_color(148, 163, 184)
pdf.cell(174, 6, "Upstream Capital Advisors  |  Confidential", align="L")

pdf.set_xy(18, 130)
pdf.set_font("Helvetica", "B", 7)
pdf.set_text_color(*GOLD)
pdf.cell(174, 5, "CONTENTS")
pdf.ln(4)

toc = [
    ("01", "Getting Started"),
    ("02", "Roles and Permissions"),
    ("03", "Dashboard"),
    ("04", "Mandates"),
    ("05", "Companies"),
    ("06", "Contacts"),
    ("07", "Schedule"),
    ("08", "Logging Outreach"),
    ("09", "Analytics"),
    ("10", "Settings"),
    ("11", "Glossary"),
]
for num, title in toc:
    pdf.set_x(22)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(*GOLD)
    pdf.cell(12, 6.5, num)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(203, 213, 225)
    pdf.cell(120, 6.5, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)


# ── 01 GETTING STARTED ───────────────────────────────────────────────────────
pdf.add_page()
pdf.h1("01", "Getting Started")

pdf.h2("Live Application")
pdf.kv("Frontend",   "https://frontend-navy-pi-11.vercel.app")
pdf.kv("API / Docs", "https://upstream-api-production-0a58.up.railway.app/docs")
pdf.ln(2)

pdf.h2("Logging In")
pdf.para(
    "Open the frontend URL in your browser. Enter your email address and password "
    "on the login screen, then click Sign In. Your session is stored in a secure "
    "browser cookie -- you will stay logged in until you sign out or the session expires."
)

pdf.h2("Login Credentials")
pdf.cred_table(
    ["Email", "Role", "Password"],
    [
        ["partner@upstream.test",  "Partner", "Passw0rd!"],
        ["analyst1@upstream.test", "Analyst", "Passw0rd!"],
        ["analyst2@upstream.test", "Analyst", "Passw0rd!"],
        ["analyst3@upstream.test", "Analyst", "Passw0rd!"],
        ["analyst4@upstream.test", "Analyst", "Passw0rd!"],
    ],
)

pdf.callout(
    "Use any analyst account (analyst1 through analyst4) to experience the "
    "day-to-day workflow. The partner account unlocks firm-wide analytics and "
    "mandate management that Analysts cannot access."
)

pdf.h2("Navigation")
pdf.para(
    "The left sidebar has six sections: Dashboard, Mandates, Companies, "
    "Contacts, Schedule, and Analytics. Click any item to navigate. "
    "Your name and role badge appear in the top-right corner."
)

pdf.h2("Signing Out")
pdf.para(
    "Click your name in the top-right corner and select Log Out. "
    "This immediately invalidates your session on the server."
)


# ── 02 ROLES ─────────────────────────────────────────────────────────────────
pdf.add_page()
pdf.h1("02", "Roles and Permissions")

pdf.para(
    "Project Upstream has two roles: Analyst and Partner. "
    "Your role is assigned by your administrator and shown as a badge next to "
    "your name in the top-right corner. It controls which mandates you can see "
    "and which actions you can take."
)

pdf.h2("Analyst")
pdf.role_block(
    "Analyst",
    "Day-to-day outreach and pipeline management",
    GRN,
    "The primary working role on the platform. Analysts see only the mandates "
    "they have been assigned to. Within those mandates they add companies, "
    "manage contacts, log every outreach interaction, and work through the "
    "daily Schedule queue. The vast majority of activity in Upstream is "
    "performed by Analysts."
)

pdf.h2("Partner")
pdf.role_block(
    "Partner",
    "Senior leadership -- full visibility and mandate management",
    INDG,
    "Partners see all mandates across the firm, not just assigned ones. They create "
    "mandates, assign Analysts to deals, and monitor firm-wide analytics including "
    "per-analyst productivity. Partners define the deal pipeline structure; "
    "Analysts execute within it."
)

pdf.h2("What Analysts Can and Cannot Do")
pdf.para("Y = permitted   N = not permitted")
pdf.perm_table(
    ["Action", "Analyst", "Partner"],
    [
        ["View assigned mandates",                  "Y", "Y"],
        ["View ALL firm mandates",                  "N", "Y"],
        ["Create, edit, or archive a mandate",      "N", "Y"],
        ["Assign analysts to a mandate",            "N", "Y"],
        ["Add / edit / archive a company",          "Y", "Y"],
        ["Add / edit / archive a contact",          "Y", "Y"],
        ["Log an outreach event",                   "Y", "Y"],
        ["View the Schedule work queue",            "Y", "Y"],
        ["View the Dashboard",                      "Y", "Y"],
        ["View Analytics -- overview and sources",  "Y", "Y"],
        ["View Analytics -- by-analyst report",     "N", "Y"],
        ["Manage team members",                     "N", "Y"],
    ],
)

pdf.callout(
    "If you cannot see a mandate you expect to find, it has not been assigned "
    "to you yet. Contact your Partner to be added."
)


# ── 03 DASHBOARD ─────────────────────────────────────────────────────────────
pdf.add_page()
pdf.h1("03", "Dashboard")

pdf.para(
    "The Dashboard is the first screen after login. It gives a real-time "
    "snapshot of outreach health across all your assigned mandates. "
    "Use it each morning to understand where to focus your day."
)

pdf.h2("KPI Cards")
pdf.para("Five headline numbers at the top of the page:")
for label, desc in [
    ("Total Companies",
     "All non-archived companies across your mandates."),
    ("Responded %",
     "Percentage of those companies that have replied to you."),
    ("Needs First Outreach",
     "Companies added to a mandate but never emailed. No active schedule yet."),
    ("Due This Week",
     "Companies where the next follow-up falls within the next 7 days."),
    ("Overdue",
     "Companies where the follow-up date has already passed. Shown in red -- prioritise these first."),
]:
    pdf.two_col(label, desc, lw=44)
pdf.ln(3)

pdf.h2("Status Mix Chart")
pdf.para(
    "A donut chart showing how your companies are distributed across the six "
    "pipeline statuses: Not Contacted, Contacted, Responded, Interested, "
    "Declined, Bounced. A healthy pipeline has the majority in Contacted or Responded."
)

pdf.h2("Response Rate by Bucket")
pdf.para(
    "A bar chart breaking down response rates by bucket label (the category "
    "tag on each company). Use it to identify which segments generate the most "
    "engagement and prioritise outreach accordingly."
)

pdf.h2("Due This Week List")
pdf.para(
    "Up to eight companies with follow-ups due in the next 7 days, ordered by "
    "urgency. Click any company name to go directly to its detail page. "
    "Click 'View all' to open the full Schedule page."
)


# ── 04 MANDATES ──────────────────────────────────────────────────────────────
pdf.add_page()
pdf.h1("04", "Mandates")

pdf.para(
    "A Mandate is a client engagement -- the top-level container for all "
    "companies, contacts, and outreach on a specific deal. "
    "Everything you do in Upstream happens within a mandate."
)

pdf.callout(
    "Analysts do not create mandates. A Partner creates the mandate and assigns "
    "you to it. Once assigned, the mandate and all its companies appear in your "
    "views automatically."
)

pdf.h2("Mandate Types")
for t, d in [
    ("Sell-Side",     "Advising a seller. Companies in the mandate are potential acquirers or buyers."),
    ("Buy-Side",      "Advising a buyer. Companies are acquisition targets."),
    ("Capital Raise", "Helping a client raise capital. Companies are potential investors."),
]:
    pdf.two_col(t, d, lw=32)
pdf.ln(3)

pdf.h2("Mandate Statuses")
for s, c, d in [
    ("ACTIVE",      GRN,           "Live engagement. All companies and schedules are active."),
    ("ON HOLD",     (180, 120, 8), "Paused. The deal is not being actively worked."),
    ("CLOSED",      DGRY,          "Successfully completed."),
    ("TERMINATED",  RED,           "Ended before completion."),
]:
    pdf.status_badge(s, c, d)
pdf.ln(3)

pdf.h2("Viewing Your Mandates")
pdf.para(
    "Click Mandates in the left sidebar. You will see only the mandates you "
    "have been assigned to. Click any mandate name to open its detail page, "
    "which shows companies, stats, and assigned team members."
)

pdf.h2("Mandate Detail Page")
pdf.bullet([
    "Stats bar  --  total companies, responded count, response rate, needs-initial count.",
    "Companies tab  --  the full list of companies with status and cadence info.",
    "Assignments tab  --  the analysts and partner assigned to this mandate.",
])


# ── 05 COMPANIES ─────────────────────────────────────────────────────────────
pdf.add_page()
pdf.h1("05", "Companies")

pdf.para(
    "Companies are the organisations you are contacting within a mandate -- "
    "Targets, Buyers, or Investors depending on the deal type. "
    "Each company has a pipeline status, a cadence schedule, and a full "
    "history of all outreach logged against it."
)

pdf.h2("Pipeline Statuses")
pdf.para("Every company moves through these statuses as outreach progresses:")
for s, c, d in [
    ("NOT CONTACTED", (51,  65,  85), "Added to the mandate. No email sent. Cadence not started."),
    ("CONTACTED",     (100,116, 139), "Initial email sent. Cadence is running. Awaiting a reply."),
    ("RESPONDED",     GRN,            "The company replied. Cadence stops automatically."),
    ("INTERESTED",    INDG,           "Positive engagement -- active discussion underway."),
    ("DECLINED",      (180,120,   8), "The company passed. Cadence stops automatically."),
    ("BOUNCED",       RED,            "Email undeliverable. Cadence stops automatically."),
]:
    pdf.status_badge(s, c, d)
pdf.ln(2)

pdf.callout(
    "You do not manually change the status. It updates automatically when you log "
    "outreach events: Initial Email sets Contacted, a Response event sets Responded, "
    "a Bounce event sets Bounced. See Section 08 for the full mapping."
)

pdf.h2("Adding a Company")
pdf.step(1, "Open the mandate", "Click Mandates in the sidebar, then open the relevant mandate.")
pdf.step(2, "Add Company", "Click the Add Company button on the mandate detail page.")
pdf.step(3, "Fill in the form",
    "Required: Company Name. "
    "Recommended: HQ city, sector/type, website, bucket label, "
    "source (Proprietary / Public / Referral / Imported), "
    "source quality (High / Medium / Low), "
    "cadence interval in days (e.g. 7 = follow up every 7 days).")
pdf.step(4, "Save", "Company is added with status Not Contacted and appears in the Schedule under 'Needs First Outreach'.")

pdf.h2("Company Detail Page")
pdf.para("Click any company name to open its detail page. Four sections:")
pdf.bullet([
    "Profile  --  all metadata: status, type, sector, geography, revenue, bucket, source.",
    "Outreach History  --  every event ever logged, in chronological order. Permanent, cannot be edited or deleted.",
    "Contacts  --  people at this company. Add and manage contacts here.",
    "Schedule  --  next due date, days remaining, or overdue indicator.",
])

pdf.h2("Editing a Company")
pdf.para(
    "Click Edit on the company detail page to update fields such as sector, "
    "geography, revenue, bucket, or source quality. "
    "The company name cannot be changed after creation."
)

pdf.h2("Archiving a Company")
pdf.para(
    "Archiving hides a company from all active views and removes it from the "
    "Schedule queue. No data is deleted -- history is fully preserved. "
    "Unarchive at any time using the archived filter in the companies list."
)


# ── 06 CONTACTS ──────────────────────────────────────────────────────────────
pdf.add_page()
pdf.h1("06", "Contacts")

pdf.para(
    "Contacts are named individuals at a company -- the specific people you "
    "email, call, or meet. Each company can have multiple contacts. "
    "One contact per company can be marked as Primary."
)

pdf.h2("Adding a Contact")
pdf.step(1, "Open the company",  "Navigate to the company detail page.")
pdf.step(2, "Contacts section",  "Scroll to the Contacts section.")
pdf.step(3, "Add Contact",       "Click the Add Contact button.")
pdf.step(4, "Fill in the form",
    "Required: First name, Last name. "
    "Optional: Title / designation, email, phone, LinkedIn URL, "
    "engagement type (Buy-Side, Sell-Side, Investor, Advisor, Other), "
    "date connected, contact mode, and remarks.")
pdf.step(5, "Save", "Contact is saved and visible on the company page immediately.")

pdf.h2("Primary Contact")
pdf.para(
    "Marking a contact as Primary flags them as the key person at that company. "
    "Only one contact per company can be primary -- marking a new one removes "
    "the flag from the previous one. "
    "The primary contact's name appears in company list views and reports, "
    "so it should be the person you are most actively engaging with."
)

pdf.h2("Editing a Contact")
pdf.para(
    "Click the edit icon next to any contact on the company detail page. "
    "All fields can be updated at any time."
)

pdf.h2("Archiving a Contact")
pdf.para(
    "Archiving a contact hides them from active views. Their outreach history "
    "is preserved. Use this when a contact has left the company or is no longer "
    "relevant -- do not delete, archive."
)


# ── 07 SCHEDULE ──────────────────────────────────────────────────────────────
pdf.add_page()
pdf.h1("07", "Schedule")

pdf.para(
    "The Schedule is your daily work queue. Open it every morning to see "
    "exactly which companies need action today. It is split into three sections "
    "ordered by urgency."
)

pdf.h2("Stats Bar")
pdf.para(
    "Four counters at the top: total active schedules, companies needing "
    "a first email, due this week, and overdue."
)

pdf.h2("Section 1  --  Needs First Outreach")
pdf.para(
    "Companies that have been added to a mandate but have never received an "
    "initial email. The cadence clock has not started for these. "
    "Send the initial email and log it (Section 08) to activate the schedule."
)

pdf.h2("Section 2  --  Due This Week")
pdf.para(
    "Companies where the next follow-up falls within 7 days, sorted by urgency "
    "(most imminent first). Each row shows the company name, status, mandate, "
    "and days until due. Click Log Outreach on any row to record the follow-up "
    "without leaving the Schedule page."
)

pdf.h2("Section 3  --  Overdue")
pdf.para(
    "Companies where the follow-up date has already passed, highlighted in red. "
    "Address these first. Logging a follow-up on an overdue company resets the "
    "clock forward from today."
)

pdf.h2("How the Cadence Works -- Step by Step")
pdf.bullet([
    "You add a company with a cadence interval of 7 days.",
    "The company appears under 'Needs First Outreach'. Clock is not running.",
    "You send the first email, then log it as an Initial Email event.",
    "The system records today as the initial date and sets the first follow-up "
      "to today + 7 days. Status changes to Contacted.",
    "In 7 days the company appears under 'Due This Week'.",
    "You follow up, log a Follow-Up event. Clock resets: next due = today + 7 days.",
    "This repeats until the company Responds, Declines, or Bounces -- at which "
      "point the cadence stops and the company leaves the queue.",
])

pdf.callout(
    "The initial email date is set permanently when you log the first Initial Email. "
    "It cannot be changed retroactively. All dates are computed in IST (UTC+5:30). "
    "Log outreach promptly to keep the cadence accurate."
)


# ── 08 LOGGING OUTREACH ──────────────────────────────────────────────────────
pdf.add_page()
pdf.h1("08", "Logging Outreach")

pdf.para(
    "Every interaction with a company must be logged as an Outreach Event. "
    "This is the core action you perform in Upstream. The event log is the "
    "permanent, append-only record of all outreach activity. "
    "Events cannot be edited or deleted after saving."
)

pdf.h2("How to Log an Event")
pdf.step(1, "Find the company",
    "Via the Schedule queue (click Log Outreach on the row), "
    "via the Companies list, via the Dashboard 'Due This Week' list, "
    "or via the company detail page directly.")
pdf.step(2, "Click Log Outreach",
    "The button is on the company detail page and on each row in the Schedule.")
pdf.step(3, "Select the event type",
    "Choose the type that matches what happened (see table below).")
pdf.step(4, "Set the date",
    "Defaults to today in IST. Back-date if you forgot to log on the day it happened.")
pdf.step(5, "Add a note",
    "Optional but strongly recommended: a brief summary of the interaction, "
    "key points raised, or next steps agreed. Visible to anyone on the mandate.")
pdf.step(6, "Save",
    "The event is appended to the company history immediately. "
    "The cadence recalculates and the Schedule updates in real time.")

pdf.h2("Event Types -- Effects on Status and Cadence")
pdf.para(
    "Choose the type that accurately reflects the interaction. "
    "The system uses the event type to update company status and cadence automatically."
)

for ev, status_change, cadence_effect, note in [
    ("Initial Email",
     "-> Contacted",
     "Starts clock",
     "First email ever sent. Can only be logged once per company."),
    ("Follow-Up",
     "No change",
     "Resets clock",
     "Any subsequent email or touch within the cadence."),
    ("Response",
     "-> Responded",
     "Stops clock",
     "Company replied. Use this the moment a reply comes in."),
    ("Bounce",
     "-> Bounced",
     "Stops clock",
     "Email undeliverable. Status changes, company leaves the queue."),
    ("Call",
     "No change",
     "Resets clock",
     "Phone call, inbound or outbound."),
    ("LinkedIn",
     "No change",
     "Resets clock",
     "LinkedIn message, InMail, or connection request."),
    ("Meeting",
     "No change",
     "Resets clock",
     "In-person or virtual meeting."),
    ("Note",
     "No change",
     "No change",
     "Internal note only. No outreach occurred. Does not affect the schedule."),
]:
    pdf.set_x(pdf.L)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*NAV)
    pdf.cell(28, 5.5, ev)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(*DGRY)
    pdf.cell(30, 5.5, status_change)
    pdf.cell(28, 5.5, cadence_effect)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(*BODY)
    pdf.multi_cell(pdf.W - 86, 5.5, note)
pdf.ln(3)

pdf.callout(
    "Initial Email can only be logged once. If you send a second email, log it "
    "as Follow-Up, not Initial Email. The system will block a second Initial Email "
    "and prompt you to correct the type."
)

pdf.h2("Correcting a Mistake")
pdf.para(
    "Events cannot be edited or deleted -- this preserves a reliable audit trail. "
    "If you logged the wrong type or wrong date, log a Note event immediately "
    "with an explanation (e.g. 'Correction: previous entry logged as Follow-Up "
    "should have been Call -- call took place on 15 Jun'). "
    "Your Partner can see all events and notes."
)

pdf.h2("After a Company Responds")
pdf.para(
    "Log a Response event. Status changes to Responded and the company leaves "
    "the Schedule queue. You can continue logging events (Call, Meeting, Note) "
    "on a Responded company to track ongoing discussions -- they will not "
    "generate new schedule reminders."
)


# ── 09 ANALYTICS ─────────────────────────────────────────────────────────────
pdf.add_page()
pdf.h1("09", "Analytics")

pdf.para(
    "The Analytics section gives a quantitative view of outreach performance. "
    "All figures are scoped to the mandates you can see."
)

pdf.h2("Overview  --  All users")
pdf.bullet([
    "Total companies and overall response rate across your mandates.",
    "Count of companies still awaiting a first email.",
    "Count of companies due this week and overdue.",
    "Status distribution -- how your pipeline breaks down across all six statuses.",
])

pdf.h2("Response Rate by Bucket  --  All users")
pdf.para(
    "Response rates broken down by bucket label. Shows which company segments "
    "or categories are generating the most engagement. "
    "Use this to prioritise which buckets to target more aggressively."
)

pdf.h2("Sources  --  All users")
pdf.para(
    "Lead source (Proprietary, Public, Referral, Imported) and source quality "
    "(High, Medium, Low) cross-referenced against response rates. "
    "Identifies which sourcing channels produce the best results."
)

pdf.h2("By Analyst  --  Partner only")
pdf.para(
    "Per-analyst breakdown of outreach volume, responses, and conversion rate. "
    "This report is visible to Partners only."
)


# ── 10 SETTINGS ──────────────────────────────────────────────────────────────
pdf.add_page()
pdf.h1("10", "Settings")

pdf.h2("Profile")
pdf.para(
    "Click your name in the top-right corner, then go to Settings. "
    "You can update your display name and change your password. "
    "Changing your password requires your current password. "
    "Your email address and role are read-only -- contact your Partner to change either."
)

pdf.h2("Password Requirements")
pdf.bullet([
    "Minimum 8 characters.",
    "At least one uppercase letter, one lowercase letter, and one number.",
    "Passwords are hashed -- no one can see your plain-text password.",
])

pdf.h2("Security")
pdf.para(
    "Your login session is stored in a secure, httpOnly browser cookie -- "
    "never accessible to browser scripts or extensions. "
    "All traffic is encrypted over HTTPS. "
    "Signing out immediately invalidates your session server-side. "
    "The database is backed up daily."
)


# ── 11 GLOSSARY ──────────────────────────────────────────────────────────────
pdf.add_page()
pdf.h1("11", "Glossary")

terms = [
    ("Mandate",          "A client engagement. Top-level container for companies, contacts, and outreach."),
    ("Company",          "An organisation being approached within a mandate (Target, Buyer, or Investor)."),
    ("Contact",          "A named individual at a company -- the person you email, call, or meet."),
    ("Outreach Event",   "A logged interaction. Permanent and append-only -- cannot be edited or deleted."),
    ("Initial Email",    "The first email sent to a company. Starts the cadence clock. Occurs once only."),
    ("Follow-Up",        "Any subsequent outreach after the initial email within the cadence schedule."),
    ("Cadence",          "The automated follow-up schedule driven by a per-company interval in days."),
    ("Cadence Interval", "Days between follow-ups, set when a company is added to a mandate."),
    ("AWAITING INITIAL", "Schedule state: no initial email yet. Clock is not running."),
    ("ACTIVE",           "Schedule state: initial email sent; cadence clock is running."),
    ("STOPPED",          "Schedule state: cadence halted (Responded, Declined, or Bounced)."),
    ("Overdue",          "A company whose next follow-up date has already passed."),
    ("Bucket",           "A grouping label on a company, used to segment analytics performance."),
    ("Source",           "How the lead was found: Proprietary, Public, Referral, or Imported."),
    ("Source Quality",   "Analyst's rating of lead quality: High, Medium, or Low."),
    ("Primary Contact",  "The key person at a company -- shown in list views and reports."),
    ("Soft Delete",      "Archiving -- data is hidden, never permanently removed. Reversible."),
    ("Firm",             "Your IB firm. All data in Upstream is scoped to your firm only."),
    ("IST",              "India Standard Time (UTC+5:30). Used for all cadence date calculations."),
    ("Analyst",          "Day-to-day role scoped to assigned mandates. Core working role on the platform."),
    ("Partner",          "Senior role with full firm visibility, mandate management, and all analytics."),
    ("KPI",              "Key Performance Indicator -- the five headline metrics on the Dashboard."),
]

alt = False
for term, defn in terms:
    alt = not alt
    bg = LGRY if alt else WHT
    pdf.set_fill_color(*bg)
    pdf.set_x(pdf.L)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(*NAV)
    pdf.cell(38, 5.5, term, fill=alt)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(*BODY)
    pdf.multi_cell(pdf.W - 38, 5.5, defn, fill=alt)

pdf.ln(8)
y0 = pdf.get_y()
pdf.set_fill_color(*NAV)
pdf.rect(0, y0, 210, 16, "F")
pdf.set_fill_color(*GOLD)
pdf.rect(0, y0, 210, 1.5, "F")
pdf.set_font("Helvetica", "B", 8)
pdf.set_text_color(*GOLD)
pdf.set_xy(pdf.L, y0 + 3)
pdf.cell(pdf.W, 5, "PROJECT UPSTREAM  |  User Guide", align="C")
pdf.set_font("Helvetica", "", 7.5)
pdf.set_text_color(148, 163, 184)
pdf.set_xy(pdf.L, y0 + 8.5)
pdf.cell(pdf.W, 5, "Upstream Capital Advisors  |  Confidential", align="C")


# ── OUTPUT ───────────────────────────────────────────────────────────────────
import os
out = r"D:\work\Qplus\Qplus_code\upstream\docs\Project_Upstream_User_Guide.pdf"
os.makedirs(os.path.dirname(out), exist_ok=True)
pdf.output(out)
print("PDF --> " + out)
