/**
 * Shared TypeScript types mirroring the backend API schemas.
 * Expanded per phase; Phase 0 only needs auth/role + the core enums for the design system.
 */

export type Role = "ANALYST" | "ASSOCIATE" | "PARTNER";

export type CompanyStatus =
  | "NOT_CONTACTED"
  | "CONTACTED"
  | "RESPONDED"
  | "INTERESTED"
  | "DECLINED"
  | "BOUNCED";

export type ScheduleStatus = "AWAITING_INITIAL" | "ACTIVE" | "STOPPED";

export type CompanyType = "TARGET" | "BUYER" | "INVESTOR";

export type SourceQuality = "HIGH" | "MEDIUM" | "LOW";

export interface Firm {
  id: number;
  name: string;
}

export interface CurrentUser {
  id: number;
  full_name: string;
  email: string;
  role: Role;
  firm: Firm;
}

/** Standard paginated list envelope (plan.md §6.2). */
export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export type Source = "PROPRIETARY" | "PUBLIC" | "REFERRAL" | "IMPORTED";

export interface PrimaryContact {
  id: number;
  contact_person: string;
  designation: string | null;
  email: string | null;
}

export interface Company {
  id: number;
  firm_id: number;
  mandate_id: number;
  company_name: string;
  hq: string | null;
  type: CompanyType;
  status: CompanyStatus;
  rationale: string | null;
  revenue_source: string | null;
  revenue_inr_cr: string | null;
  headcount: number | null;
  website: string | null;
  linkedin: string | null;
  relevant_investments: string | null;
  bucket: string | null;
  source: Source;
  source_quality: SourceQuality;
  created_by_id: number | null;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
  // Computed cadence fields (server-side only)
  schedule_status: ScheduleStatus | null;
  initial_date: string | null;
  next_due_date: string | null;
  days_remaining: number | null;
  is_overdue: boolean;
  primary_contact: PrimaryContact | null;
}

export interface CompanySummary {
  responded_pct: number;
  overdue_count: number;
  needs_initial_count: number;
  by_status: Record<CompanyStatus, number>;
}

export interface CompanyListResponse {
  items: Company[];
  total: number;
  page: number;
  page_size: number;
  summary: CompanySummary;
}

export interface Contact {
  id: number;
  firm_id: number;
  company_id: number;
  contact_person: string;
  designation: string | null;
  email: string | null;
  phone: string | null;
  linkedin: string | null;
  reason: string | null;
  engagement: string | null;
  date_connected: string | null;
  mode: string | null;
  poc_owner_id: number | null;
  remark: string | null;
  comments: string | null;
  is_primary: boolean;
  last_contact_date: string | null;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface OutreachEvent {
  id: number;
  firm_id: number;
  company_id: number;
  schedule_id: number | null;
  contact_id: number | null;
  event_type: string;
  occurred_on: string;
  regarding: string | null;
  notes: string | null;
  owner_id: number | null;
  created_at: string;
}

export interface OutreachSchedule {
  id: number;
  firm_id: number;
  company_id: number;
  status: ScheduleStatus;
  initial_date: string | null;
  cadence_interval_days: number;
  regarding: string | null;
  stopped_reason: string | null;
  stopped_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface DuplicateWarning {
  company_id: number;
  company_name: string;
  mandate_id: number;
  status: CompanyStatus;
  initial_date: string | null;
}

export interface CompanyDetail extends Company {
  contacts: Contact[];
  events: OutreachEvent[];
  schedule: OutreachSchedule | null;
  duplicate_warnings: DuplicateWarning[];
}

export interface ContactDetail extends Contact {
  events: OutreachEvent[];
}

export interface ContactListResponse {
  items: Contact[];
  total: number;
}

// ── Mandates (Phase 7) ────────────────────────────────────────────────────────

export type MandateType = "SELL_SIDE" | "BUY_SIDE" | "CAPITAL_RAISE";
export type MandateStatus = "ACTIVE" | "ON_HOLD" | "CLOSED" | "TERMINATED";

export interface MandateStats {
  total: number;
  responded: number;
  needs_initial: number;
  responded_pct: number;
}

export interface Mandate {
  id: number;
  firm_id: number;
  client_name: string;
  name: string;
  type: MandateType;
  status: MandateStatus;
  exchange_rate: string | null;
  exchange_rate_date: string | null;
  lead_owner_id: number | null;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface MandateListItem extends Mandate, MandateStats {}

export interface MandateAssignmentUser {
  id: number;
  full_name: string;
  email: string;
  role: Role;
}

export interface MandateDetail extends Mandate {
  stats: MandateStats;
  assignments: MandateAssignmentUser[];
  lead_owner: { id: number; full_name: string; email: string } | null;
}

export interface FirmUser {
  id: number;
  full_name: string;
  email: string;
  role: Role;
}
