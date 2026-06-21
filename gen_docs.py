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

    def kv(self, label, value, bold_val=False):
        self.set_x(self.L)
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(*DGRY)
        self.cell(42, 5.5, label)
        self.set_font("Helvetica", "B" if bold_val else "", 9.5)
        self.set_text_color(*BODY)
        self.multi_cell(self.W - 42, 5.5, value)

    def perm_table(self, headers, rows):
        cw = [self.W - 54, 18, 18, 18]
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

    def status_badge(self, label, colour, desc):
        y = self.get_y() + 1
        self.set_fill_color(*colour)
        self.rect(self.L, y, 24, 5, "F")
        self.set_font("Helvetica", "B", 7)
        self.set_text_color(*WHT)
        self.set_xy(self.L, y)
        self.cell(24, 5, label, align="C")
        self.set_x(self.L + 27)
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*BODY)
        self.multi_cell(self.W - 27, 5.5, desc)
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

    def role_chip(self, role, colour, desc):
        y = self.get_y()
        self.set_fill_color(*colour)
        self.rect(self.L, y + 1, 3, 9, "F")
        self.set_x(self.L + 6)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*colour)
        self.cell(34, 5, role)
        self.set_x(self.L + 40)
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*BODY)
        self.multi_cell(self.W - 40, 5, desc)
        self.ln(2.5)


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

# monogram block
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

# TOC on dark lower panel
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
    # dotted leader line
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(120, 6.5, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)


# ── 01 GETTING STARTED ───────────────────────────────────────────────────────
pdf.add_page()
pdf.h1("01", "Getting Started")

pdf.h2("Live Application")
pdf.kv("Frontend",  "https://frontend-navy-pi-11.vercel.app")
pdf.kv("API / Docs","https://upstream-api-production-0a58.up.railway.app/docs")
pdf.ln(2)

pdf.h2("Login")
pdf.para(
    "Navigate to the frontend URL. Enter your email and password on the login screen. "
    "Sessions persist in a secure browser cookie -- no manual token management required."
)

pdf.h2("Login Credentials")
pdf.perm_table(
    ["Email", "Role", "Password", ""],
    [
        ["partner@upstream.test",    "Partner",   "Passw0rd!", ""],
        ["analyst1@upstream.test",   "Analyst",   "Passw0rd!", ""],
        ["analyst2@upstream.test",   "Analyst",   "Passw0rd!", ""],
        ["associate1@upstream.test", "Associate", "Passw0rd!", ""],
        ["associate2@upstream.test", "Associate", "Passw0rd!", ""],
    ],
)

pdf.callout(
    "The Partner account has full access to all mandates, analytics, and team "
    "management. Analyst and Associate accounts show only their assigned mandates."
)

pdf.h2("Signing Out")
pdf.para("Click your name in the top-right corner and select Sign Out.")


# ── 02 ROLES ─────────────────────────────────────────────────────────────────
pdf.add_page()
pdf.h1("02", "Roles and Permissions")

pdf.para(
    "Each user is assigned one role. The role governs mandate visibility and "
    "available actions. All data is firm-scoped -- no information is shared "
    "across different firms."
)

pdf.h2("Roles")
pdf.role_chip("Partner",   INDG, "Full visibility. Manages mandates, assigns team, views firm-wide analytics.")
pdf.role_chip("Associate", GRN,  "Assigned mandates only. Manages companies, contacts, and outreach.")
pdf.role_chip("Analyst",   (251, 146, 60), "Assigned mandates only. Manages companies, contacts, and outreach.")

pdf.h2("Permission Matrix")
pdf.perm_table(
    ["Action", "Partner", "Assoc.", "Analyst"],
    [
        ["View all mandates",                  "Y", "N", "N"],
        ["View assigned mandates",             "Y", "Y", "Y"],
        ["Create / edit / archive mandate",    "Y", "N", "N"],
        ["Assign team members to mandate",     "Y", "N", "N"],
        ["Add / edit / archive company",       "Y", "Y", "Y"],
        ["Add / edit / archive contact",       "Y", "Y", "Y"],
        ["Log outreach events",                "Y", "Y", "Y"],
        ["View Schedule work queue",           "Y", "Y", "Y"],
        ["View Dashboard",                     "Y", "Y", "Y"],
        ["View Analytics -- overview",         "Y", "Y", "Y"],
        ["View Analytics -- by-analyst",       "Y", "N", "N"],
        ["Manage team members",                "Y", "N", "N"],
    ],
)


# ── 03 DASHBOARD ─────────────────────────────────────────────────────────────
pdf.add_page()
pdf.h1("03", "Dashboard")

pdf.para(
    "The Dashboard is the opening screen after login. It summarises outreach "
    "health across all visible mandates in real time."
)

pdf.h2("KPI Cards")
for label, desc in [
    ("Total Companies",      "All non-archived companies across visible mandates."),
    ("Responded %",          "Percentage of companies that have replied."),
    ("Needs First Outreach", "Companies with no initial email sent yet."),
    ("Due This Week",        "Follow-ups falling within the next 7 days."),
    ("Overdue",              "Follow-ups past their due date. Displayed in red."),
]:
    pdf.two_col(label, desc)
pdf.ln(3)

pdf.h2("Charts")
pdf.h3("Status Mix (Donut)")
pdf.para(
    "Displays the distribution of companies across all six pipeline statuses "
    "(Not Contacted, Contacted, Responded, Interested, Declined, Bounced)."
)
pdf.h3("Response Rate by Bucket (Bar)")
pdf.para(
    "Shows response rates segmented by company bucket label, helping identify "
    "which categories generate the highest engagement."
)

pdf.h2("Due This Week")
pdf.para(
    "A list of up to 8 companies with follow-ups due this week, ordered by urgency. "
    "Click any company name to open its detail page."
)


# ── 04 MANDATES ──────────────────────────────────────────────────────────────
pdf.add_page()
pdf.h1("04", "Mandates")

pdf.para(
    "A Mandate is a deal or client engagement. All companies, contacts, and "
    "outreach activity belong to a mandate."
)

pdf.h2("Types")
for t, d in [
    ("Sell-Side",     "Advising a seller. Companies in the mandate are potential buyers."),
    ("Buy-Side",      "Advising a buyer. Companies are acquisition targets."),
    ("Capital Raise", "Helping a client raise capital. Companies are potential investors."),
]:
    pdf.two_col(t, d)
pdf.ln(3)

pdf.h2("Statuses")
for s, c, d in [
    ("ACTIVE",      GRN,           "Live and active."),
    ("ON HOLD",     (180, 120, 8), "Paused."),
    ("CLOSED",      DGRY,          "Completed successfully."),
    ("TERMINATED",  RED,           "Ended before completion."),
]:
    pdf.status_badge(s, c, d)
pdf.ln(3)

pdf.h2("Creating a Mandate  (Partner)")
pdf.step(1, "Mandates", "Click Mandates in the left navigation.")
pdf.step(2, "New Mandate", "Enter the name, type, and optional description.")
pdf.step(3, "Save", "Mandate is created and visible in the list.")
pdf.step(4, "Assign team", "Open the mandate, go to Assignments, and add team members.")

pdf.h2("Archiving")
pdf.para(
    "Archiving hides a mandate and all its companies from active views and the "
    "work queue. No data is deleted. Unarchive at any time."
)


# ── 05 COMPANIES ─────────────────────────────────────────────────────────────
pdf.add_page()
pdf.h1("05", "Companies")

pdf.para(
    "Companies are the organisations being contacted within a mandate -- "
    "Targets, Buyers, or Investors depending on the mandate type."
)

pdf.h2("Pipeline Statuses")
for s, c, d in [
    ("NOT CONTACTED", (51,  65, 85),  "Added; no outreach yet."),
    ("CONTACTED",     (100,116,139),  "Initial email sent; awaiting reply."),
    ("RESPONDED",     GRN,            "Has replied. Cadence stops."),
    ("INTERESTED",    INDG,           "Positive signal; active discussion."),
    ("DECLINED",      (180,120,  8),  "Passed. Cadence stops."),
    ("BOUNCED",       RED,            "Email bounced. Cadence stops."),
]:
    pdf.status_badge(s, c, d)
pdf.ln(3)

pdf.h2("Adding a Company")
pdf.para(
    "Open a mandate and click Add Company. Required: company name. "
    "Optional: sector, geography, revenue range, bucket, source, source quality, "
    "and cadence interval (days between follow-ups, e.g. 7)."
)

pdf.h2("Company Detail Page")
pdf.bullet([
    "Profile -- name, status, type, sector, geography, revenue range.",
    "Outreach History -- permanent, chronological event log. Cannot be edited or deleted.",
    "Contacts -- people at this company.",
    "Cadence -- next due date, days remaining, or overdue indicator.",
])

pdf.h2("Source and Source Quality")
pdf.para(
    "Tracks lead origin (Proprietary, Public, Referral, Imported) and quality "
    "(High, Medium, Low). These fields power the Analytics Sources report."
)


# ── 06 CONTACTS ──────────────────────────────────────────────────────────────
pdf.add_page()
pdf.h1("06", "Contacts")

pdf.para(
    "Contacts are named individuals at a company -- the people you email, call, "
    "or message. Each contact can store title, email, phone, and LinkedIn URL."
)

pdf.h2("Adding a Contact")
pdf.para(
    "From a Company detail page, scroll to Contacts and click Add Contact. "
    "Required: first and last name. Optional: title, email, phone, LinkedIn URL, "
    "engagement type (Buy-Side, Sell-Side, Investor, Advisor, Other)."
)

pdf.h2("Primary Contact")
pdf.para(
    "Mark one contact per company as Primary. Their name surfaces in company list "
    "views and reports. Only one primary contact per company is permitted."
)

pdf.h2("Archiving")
pdf.para("Archiving a contact hides them from active views without deleting the record.")


# ── 07 SCHEDULE ──────────────────────────────────────────────────────────────
pdf.add_page()
pdf.h1("07", "Schedule")

pdf.para(
    "The Schedule is the daily work queue. It surfaces every company that "
    "requires action, split across three sections."
)

pdf.h2("Needs First Outreach")
pdf.para(
    "Companies with no initial email on record. The cadence clock has not started. "
    "Send the first email and log it to activate the schedule."
)

pdf.h2("Due  (next 7 days)")
pdf.para(
    "Contacted companies whose next follow-up falls within 7 days. "
    "Sorted by urgency, most imminent first."
)

pdf.h2("Overdue")
pdf.para("Follow-ups past their due date, highlighted in red. Immediate action required.")

pdf.h2("How the Cadence Works")
pdf.para(
    "Logging the first Initial Email starts the clock. The system adds the cadence "
    "interval (e.g. 7 days) to the last event date to compute the next due date. "
    "Each subsequent log resets the clock forward. The clock stops automatically "
    "when a company reaches Responded, Declined, or Bounced."
)

pdf.callout(
    "Dates are computed in IST (UTC+5:30). The initial-email date is fixed permanently "
    "once set -- it cannot be changed retroactively."
)

pdf.h2("Stats Bar")
pdf.para(
    "Four counters at the top of the page: total active schedules, "
    "needing initial outreach, due this week, and overdue."
)


# ── 08 LOGGING OUTREACH ──────────────────────────────────────────────────────
pdf.add_page()
pdf.h1("08", "Logging Outreach")

pdf.para(
    "Every interaction with a company is recorded as an Outreach Event -- "
    "the permanent, append-only history of all outreach activity."
)

pdf.h2("Event Types")
for ev, desc in [
    ("Initial Email", "First email ever sent. Starts the cadence. Occurs once."),
    ("Follow-Up",     "Any subsequent email or touch within the cadence."),
    ("Response",      "Company replied. Status -> Responded. Cadence stops."),
    ("Bounce",        "Email bounced. Status -> Bounced. Cadence stops."),
    ("Call",          "Phone call (inbound or outbound)."),
    ("LinkedIn",      "LinkedIn message, InMail, or connection."),
    ("Meeting",       "In-person or virtual meeting."),
    ("Note",          "Internal note. No outreach occurred; no status change."),
]:
    pdf.two_col(ev, desc, lw=30)
pdf.ln(3)

pdf.h2("Logging an Event")
pdf.step(1, "Open the company",  "Via Schedule, Companies list, or Dashboard.")
pdf.step(2, "Log Outreach",      "Button on the company detail page or each Schedule row.")
pdf.step(3, "Select event type", "Choose from the dropdown.")
pdf.step(4, "Set the date",      "Defaults to today. Back-date if needed.")
pdf.step(5, "Add a note",        "Optional free-text context or summary.")
pdf.step(6, "Save",              "Event appended immediately. Cadence recalculates.")

pdf.h2("Immutability")
pdf.para(
    "Events cannot be edited or deleted after saving. This preserves an accurate "
    "audit trail. To correct an error, log a Note event with the correction."
)

pdf.h2("Status Auto-Updates")
pdf.bullet([
    "Initial Email  -->  Contacted",
    "Response       -->  Responded  (cadence stops)",
    "Bounce         -->  Bounced    (cadence stops)",
    "Follow-Up / Call / LinkedIn / Meeting  -->  no change (stays Contacted)",
    "Note           -->  no change",
])


# ── 09 ANALYTICS ─────────────────────────────────────────────────────────────
pdf.add_page()
pdf.h1("09", "Analytics")

pdf.para("All analytics are scoped to the user's visible mandates.")

pdf.h2("Overview  (all roles)")
pdf.bullet([
    "Total companies and overall response rate.",
    "Count pending first contact.",
    "Due-this-week and overdue counts.",
    "Status distribution across the pipeline.",
])

pdf.h2("Response Rate by Bucket  (all roles)")
pdf.para(
    "Response rates segmented by company bucket label. Identifies which segments "
    "or deal types produce the highest engagement."
)

pdf.h2("By Analyst  (Partner only)")
pdf.para(
    "Per-analyst and per-associate breakdown of outreach volume, responses secured, "
    "and conversion rate. Used to monitor productivity and balance workload."
)

pdf.h2("Sources  (all roles)")
pdf.para(
    "Lead source (Proprietary, Public, Referral, Imported) and quality "
    "(High, Medium, Low) cross-referenced against response rates. "
    "Guides business development prioritisation."
)


# ── 10 SETTINGS ──────────────────────────────────────────────────────────────
pdf.add_page()
pdf.h1("10", "Settings")

pdf.h2("Profile")
pdf.para(
    "Update your display name and change your password (current password required). "
    "Your email address and role are read-only and set by your administrator."
)

pdf.h2("Team  (Partner only)")
pdf.para(
    "View all team members, their roles, and mandate assignments. "
    "Invitation and role-change functionality is on the product roadmap."
)

pdf.h2("Security")
pdf.para(
    "Passwords are hashed with bcrypt. Auth tokens are stored in secure httpOnly "
    "cookies -- never in browser storage. All connections are HTTPS. "
    "The database is backed up daily."
)

pdf.callout(
    "All data is firm-scoped and isolated. No information is shared "
    "between firms, regardless of which accounts are active."
)


# ── 11 GLOSSARY ──────────────────────────────────────────────────────────────
pdf.add_page()
pdf.h1("11", "Glossary")

terms = [
    ("Mandate",          "A deal or engagement. Top-level container for companies, contacts, and outreach."),
    ("Company",          "An organisation being approached within a mandate (Target, Buyer, or Investor)."),
    ("Contact",          "A named individual at a company."),
    ("Outreach Event",   "A recorded interaction (email, call, meeting, note). Permanent and append-only."),
    ("Initial Email",    "The first email to a company. Starts the cadence clock. Occurs once only."),
    ("Follow-Up",        "Any outreach after the initial email within the cadence schedule."),
    ("Cadence",          "The automated follow-up schedule, driven by a per-company interval in days."),
    ("Cadence Interval", "Days between follow-ups, set when a company is added to a mandate."),
    ("AWAITING INITIAL", "Schedule state: no initial email yet. Clock not started."),
    ("ACTIVE",           "Schedule state: initial email sent; cadence clock running."),
    ("STOPPED",          "Schedule state: cadence halted (Responded, Declined, or Bounced)."),
    ("Overdue",          "A company whose next follow-up date has passed."),
    ("Bucket",           "A grouping label applied to a company; used in analytics segmentation."),
    ("Source",           "Lead origin: Proprietary, Public, Referral, or Imported."),
    ("Source Quality",   "Analyst's rating of lead quality: High, Medium, or Low."),
    ("Firm",             "The IB firm using Upstream. All data is scoped to one firm."),
    ("Soft Delete",      "Archiving -- data is hidden, not permanently removed."),
    ("IST",              "India Standard Time (UTC+5:30). Used for all cadence calculations."),
    ("Partner",          "Role with full visibility, mandate management, and firm-wide analytics."),
    ("Analyst",          "Role scoped to assigned mandates. Logs outreach and manages companies."),
    ("Associate",        "Same scope as Analyst."),
    ("Primary Contact",  "The designated key person at a company; shown prominently in list views."),
    ("KPI",              "Key Performance Indicator -- the headline metrics on the Dashboard."),
]

alt = False
for term, defn in terms:
    alt = not alt
    bg = LGRY if alt else WHT
    self_x = pdf.L
    pdf.set_fill_color(*bg)
    pdf.set_x(self_x)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(*NAV)
    pdf.cell(36, 5.5, term, fill=alt)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(*BODY)
    pdf.multi_cell(pdf.W - 36, 5.5, defn, fill=alt)

# closing band
pdf.ln(8)
pdf.set_fill_color(*NAV)
pdf.set_x(0)
bh = 16
y0 = pdf.get_y()
pdf.rect(0, y0, 210, bh, "F")
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
out = r"D:\work\Qplus\Qplus_code\upstream\docs\Project_Upstream_User_Guide.pdf"
import os; os.makedirs(os.path.dirname(out), exist_ok=True)
pdf.output(out)
print("PDF --> " + out)
