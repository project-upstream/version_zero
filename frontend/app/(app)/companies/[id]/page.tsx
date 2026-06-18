"use client";

import { use } from "react";
import { useRouter } from "next/navigation";
import {
  ArrowLeft,
  Globe,
  ExternalLink,
  MapPin,
  Users,
  AlertTriangle,
  Archive,
  ArchiveRestore,
} from "lucide-react";
import { toast } from "sonner";

import { useCompany, useArchiveCompany, useUnarchiveCompany } from "@/hooks/use-companies";
import { usePatchSchedule } from "@/hooks/use-schedule";
import { useBenchmark } from "@/hooks/use-analytics";
import { StatusBadge } from "@/components/features/status-badge";
import { CadenceBadge, cadenceStateFromSchedule } from "@/components/features/status-badge";
import { LogOutreachDialog } from "@/components/features/log-outreach-dialog";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ContactDialog } from "@/components/features/contact-dialog";
import type { CompanyDetail, Contact, OutreachEvent } from "@/types";

// ── Field display ────────────────────────────────────────────────────────────

function Field({ label, value }: { label: string; value: React.ReactNode }) {
  if (value === null || value === undefined || value === "") return null;
  return (
    <div>
      <dt className="text-xs text-muted-foreground uppercase tracking-wide">{label}</dt>
      <dd className="mt-0.5 text-sm">{value}</dd>
    </div>
  );
}

// ── Benchmark strip ──────────────────────────────────────────────────────────

function BenchmarkStrip({ companyId }: { companyId: number }) {
  const { data: bm } = useBenchmark(companyId);
  if (!bm) return null;

  return (
    <div className="flex flex-wrap gap-4 rounded-lg border bg-muted/30 px-4 py-3 text-sm">
      <span>
        <span className="font-medium">{bm.this_company_touches}</span>
        <span className="text-muted-foreground"> touches</span>
        {bm.mandate_avg_touches_to_response != null && (
          <span className="text-muted-foreground"> · mandate avg {bm.mandate_avg_touches_to_response}</span>
        )}
      </span>
      {bm.this_company_days_to_response != null && (
        <span>
          <span className="font-medium">responded in {bm.this_company_days_to_response}d</span>
          {bm.mandate_avg_days_to_response != null && (
            <span className="text-muted-foreground"> · avg {bm.mandate_avg_days_to_response}d</span>
          )}
        </span>
      )}
      <span className="ml-auto text-muted-foreground">
        Mandate response rate: {Math.round(bm.mandate_response_rate * 100)}%
      </span>
    </div>
  );
}

// ── Duplicate warning banner ─────────────────────────────────────────────────

function DuplicateBanner({ warnings }: { warnings: CompanyDetail["duplicate_warnings"] }) {
  if (!warnings.length) return null;
  return (
    <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 dark:border-amber-800/50 dark:bg-amber-950/20">
      <div className="flex items-start gap-2">
        <AlertTriangle className="mt-0.5 h-4 w-4 flex-shrink-0 text-amber-600" />
        <div>
          <p className="text-sm font-medium text-amber-800 dark:text-amber-200">
            Possible duplicate{warnings.length > 1 ? "s" : ""} across mandates
          </p>
          <ul className="mt-1 space-y-0.5">
            {warnings.map((w) => (
              <li key={w.company_id} className="text-xs text-amber-700 dark:text-amber-300">
                {w.company_name} (mandate {w.mandate_id}) — <StatusBadge status={w.status} />
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

// ── Contacts tab ─────────────────────────────────────────────────────────────

function ContactsTab({ contacts, companyId }: { contacts: Contact[]; companyId: number }) {
  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <ContactDialog companyId={companyId} />
      </div>
      {contacts.length === 0 ? (
        <p className="py-8 text-center text-sm text-muted-foreground">No contacts yet.</p>
      ) : (
        <div className="divide-y">
          {contacts.map((c) => (
            <div key={c.id} className="flex items-start justify-between py-4 gap-4">
              <div>
                <p className="font-medium text-sm">
                  {c.contact_person}
                  {c.is_primary && (
                    <Badge variant="secondary" className="ml-2 text-[10px]">Primary</Badge>
                  )}
                </p>
                {c.designation && (
                  <p className="text-xs text-muted-foreground">{c.designation}</p>
                )}
              </div>
              <div className="flex items-center gap-2 text-right text-xs text-muted-foreground shrink-0">
                <div>
                  {c.email && <p>{c.email}</p>}
                  {c.phone && <p>{c.phone}</p>}
                </div>
                <ContactDialog
                  companyId={companyId}
                  contact={c}
                  trigger={
                    <button className="rounded px-2 py-1 text-xs text-muted-foreground hover:bg-muted hover:text-foreground">
                      Edit
                    </button>
                  }
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Timeline tab ─────────────────────────────────────────────────────────────

const EVENT_TYPE_LABELS: Record<string, string> = {
  INITIAL_EMAIL: "Initial email",
  FOLLOW_UP: "Follow-up",
  RESPONSE: "Response",
  BOUNCE: "Bounce",
  CALL: "Call",
  LINKEDIN: "LinkedIn",
  MEETING: "Meeting",
  NOTE: "Note",
};

function TimelineTab({ events }: { events: OutreachEvent[] }) {
  if (!events.length)
    return (
      <p className="py-8 text-center text-sm text-muted-foreground">No outreach events yet.</p>
    );

  return (
    <ol className="relative ml-3 border-l border-border">
      {events.map((e) => (
        <li key={e.id} className="mb-6 ml-4">
          <div className="absolute -left-1.5 mt-1.5 h-3 w-3 rounded-full bg-border" />
          <time className="text-xs text-muted-foreground">{e.occurred_on}</time>
          <p className="text-sm font-medium">
            {EVENT_TYPE_LABELS[e.event_type] ?? e.event_type}
          </p>
          {e.notes && <p className="text-xs text-muted-foreground mt-0.5">{e.notes}</p>}
        </li>
      ))}
    </ol>
  );
}

// ── Overview tab ─────────────────────────────────────────────────────────────

function OverviewTab({ company }: { company: CompanyDetail }) {
  return (
    <div className="grid gap-6 sm:grid-cols-2">
      <Card>
        <CardHeader><CardTitle className="text-sm">Company details</CardTitle></CardHeader>
        <CardContent>
          <dl className="grid grid-cols-2 gap-x-4 gap-y-3">
            <Field label="Type" value={company.type} />
            <Field label="Status" value={<StatusBadge status={company.status} />} />
            <Field label="HQ" value={company.hq} />
            <Field label="Headcount" value={company.headcount?.toLocaleString()} />
            <Field label="Revenue (INR Cr)" value={company.revenue_inr_cr} />
            <Field label="Revenue source" value={company.revenue_source} />
            <Field label="Source" value={company.source} />
            <Field label="Source quality" value={company.source_quality} />
            <Field label="Bucket" value={company.bucket} />
          </dl>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-sm">Outreach schedule</CardTitle></CardHeader>
        <CardContent>
          <dl className="grid grid-cols-2 gap-x-4 gap-y-3">
            <Field label="Schedule status" value={
              company.schedule_status ? (
                <CadenceBadge
                  state={cadenceStateFromSchedule({
                    scheduleStatus: company.schedule_status,
                    daysRemaining: company.days_remaining,
                  })}
                />
              ) : null
            } />
            <Field label="Initial date" value={company.initial_date} />
            <Field label="Next due" value={company.next_due_date} />
            <Field label="Days remaining" value={
              company.days_remaining !== null ? String(company.days_remaining) : undefined
            } />
            {company.schedule?.regarding && (
              <Field label="Regarding" value={company.schedule.regarding} />
            )}
            {company.schedule?.stopped_reason && (
              <Field label="Stopped reason" value={company.schedule.stopped_reason} />
            )}
          </dl>
        </CardContent>
      </Card>

      {(company.rationale || company.relevant_investments) && (
        <Card className="sm:col-span-2">
          <CardHeader><CardTitle className="text-sm">Notes</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {company.rationale && (
              <Field label="Rationale" value={<p className="text-sm">{company.rationale}</p>} />
            )}
            {company.relevant_investments && (
              <Field label="Relevant investments" value={<p className="text-sm">{company.relevant_investments}</p>} />
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// ── Cadence tab ──────────────────────────────────────────────────────────────

function CadenceTab({ company }: { company: CompanyDetail }) {
  const patchSchedule = usePatchSchedule(company.id);
  const sched = company.schedule;
  const isStopped = sched?.status === "STOPPED";
  const canResume = isStopped && sched?.stopped_reason === "MANUAL";
  const isActive = sched?.status === "ACTIVE";

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm">Schedule configuration</CardTitle>
            <div className="flex gap-2">
              {isActive && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => patchSchedule.mutate({ action: "pause" })}
                >
                  Pause
                </Button>
              )}
              {canResume && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => patchSchedule.mutate({ action: "resume" })}
                >
                  Resume
                </Button>
              )}
              <LogOutreachDialog
                companyId={company.id}
                companyName={company.company_name}
                defaultEventType={
                  company.schedule_status === "AWAITING_INITIAL"
                    ? "INITIAL_EMAIL"
                    : "FOLLOW_UP"
                }
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <dl className="grid grid-cols-2 gap-x-6 gap-y-4">
            <Field
              label="Status"
              value={
                company.schedule_status ? (
                  <CadenceBadge
                    state={cadenceStateFromSchedule({
                      scheduleStatus: company.schedule_status,
                      daysRemaining: company.days_remaining,
                    })}
                  />
                ) : null
              }
            />
            <Field label="Initial date (read-only)" value={company.initial_date ?? "Not set yet"} />
            <Field label="Interval (days)" value={sched ? String(sched.cadence_interval_days) : "—"} />
            <Field label="Next follow-up due" value={company.next_due_date ?? "—"} />
            <Field
              label="Days remaining"
              value={
                company.days_remaining !== null
                  ? `${company.days_remaining}d`
                  : "—"
              }
            />
            {sched?.regarding && <Field label="Regarding" value={sched.regarding} />}
            {sched?.stopped_reason && (
              <Field label="Stopped reason" value={sched.stopped_reason} />
            )}
            {sched?.stopped_at && (
              <Field label="Stopped at" value={new Date(sched.stopped_at).toLocaleDateString()} />
            )}
          </dl>
        </CardContent>
      </Card>
    </div>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function CompanyDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();
  const { data: company, isLoading, error } = useCompany(Number(id));
  const archive = useArchiveCompany();
  const unarchive = useUnarchiveCompany();

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="h-8 w-48 animate-pulse rounded-md bg-muted mb-4" />
        <div className="h-4 w-64 animate-pulse rounded-md bg-muted" />
      </div>
    );
  }

  if (error || !company) {
    return (
      <div className="p-6">
        <p className="text-sm text-muted-foreground">Company not found.</p>
      </div>
    );
  }

  const cadenceState = company.schedule_status
    ? cadenceStateFromSchedule({
        scheduleStatus: company.schedule_status,
        daysRemaining: company.days_remaining,
      })
    : null;

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Back + actions */}
      <div className="flex items-center justify-between">
        <Button variant="ghost" size="sm" onClick={() => router.back()}>
          <ArrowLeft className="mr-1 h-4 w-4" />
          Back
        </Button>
        <div className="flex items-center gap-2">
          {company.archived_at ? (
            <>
              <Badge variant="secondary">Archived</Badge>
              <Button
                variant="outline"
                size="sm"
                onClick={async () => {
                  try {
                    await unarchive.mutateAsync(company.id);
                    toast.success("Company restored");
                  } catch {
                    toast.error("Failed to restore company");
                  }
                }}
              >
                <ArchiveRestore className="mr-1 h-4 w-4" />
                Restore
              </Button>
            </>
          ) : (
            <Button
              variant="outline"
              size="sm"
              onClick={async () => {
                if (!confirm("Archive this company? Data is kept, not destroyed.")) return;
                try {
                  await archive.mutateAsync(company.id);
                  toast.success("Company archived");
                  router.back();
                } catch {
                  toast.error("Failed to archive company");
                }
              }}
            >
              <Archive className="mr-1 h-4 w-4" />
              Archive
            </Button>
          )}
        </div>
      </div>

      {/* Header */}
      <div className="flex flex-wrap items-start gap-3">
        <div className="flex-1 min-w-0">
          <h1 className="text-xl font-semibold truncate">{company.company_name}</h1>
          <div className="mt-1 flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
            {company.hq && (
              <span className="flex items-center gap-1">
                <MapPin className="h-3 w-3" /> {company.hq}
              </span>
            )}
            {company.headcount && (
              <span className="flex items-center gap-1">
                <Users className="h-3 w-3" /> {company.headcount.toLocaleString()}
              </span>
            )}
            {company.website && (
              <a
                href={company.website}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 hover:text-foreground"
              >
                <Globe className="h-3 w-3" /> Website
              </a>
            )}
            {company.linkedin && (
              <a
                href={company.linkedin}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 hover:text-foreground"
              >
                <ExternalLink className="h-3 w-3" /> LinkedIn
              </a>
            )}
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <StatusBadge status={company.status} />
          {cadenceState && (
            <CadenceBadge
              state={cadenceState}
              label={
                company.is_overdue
                  ? `${Math.abs(company.days_remaining!)}d overdue`
                  : company.days_remaining !== null
                  ? `due in ${company.days_remaining}d`
                  : undefined
              }
            />
          )}
        </div>
      </div>

      {/* Benchmark strip */}
      <BenchmarkStrip companyId={company.id} />

      {/* Duplicate warning */}
      <DuplicateBanner warnings={company.duplicate_warnings} />

      {/* Tabs */}
      <Tabs defaultValue="overview">
        <div className="flex items-center justify-between">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="cadence">Cadence</TabsTrigger>
            <TabsTrigger value="contacts">
              Contacts ({company.contacts.length})
            </TabsTrigger>
            <TabsTrigger value="timeline">
              Timeline ({company.events.length})
            </TabsTrigger>
          </TabsList>
          {!company.archived_at && (
            <LogOutreachDialog
              companyId={company.id}
              companyName={company.company_name}
              defaultEventType={
                company.schedule_status === "AWAITING_INITIAL"
                  ? "INITIAL_EMAIL"
                  : "FOLLOW_UP"
              }
            />
          )}
        </div>

        <TabsContent value="overview" className="mt-4">
          <OverviewTab company={company} />
        </TabsContent>

        <TabsContent value="cadence" className="mt-4">
          <CadenceTab company={company} />
        </TabsContent>

        <TabsContent value="contacts" className="mt-4">
          <ContactsTab contacts={company.contacts} companyId={company.id} />
        </TabsContent>

        <TabsContent value="timeline" className="mt-4">
          <TimelineTab events={company.events} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
