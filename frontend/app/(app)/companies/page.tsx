"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Search, Filter, Building2, AlertTriangle } from "lucide-react";

import { useCompanies, type CompanyFilters } from "@/hooks/use-companies";
import { CompanyDialog } from "@/components/features/company-dialog";
import { DataTable, type Column } from "@/components/features/data-table";
import { StatusBadge } from "@/components/features/status-badge";
import { CadenceBadge, cadenceStateFromSchedule } from "@/components/features/status-badge";
import { StatCard } from "@/components/features/stat-card";
import { EmptyState } from "@/components/features/empty-state";
import { PageHeader } from "@/components/layout/page-header";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import type { Company, CompanyStatus, CompanyType } from "@/types";

const SOURCE_DOT: Record<string, string> = {
  PROPRIETARY: "bg-violet-500",
  PUBLIC: "bg-sky-400",
  REFERRAL: "bg-emerald-500",
  IMPORTED: "bg-gray-400",
};

const PAGE_SIZE = 25;

const STATUS_OPTIONS: { label: string; value: CompanyStatus | "" }[] = [
  { label: "All statuses", value: "" },
  { label: "Not contacted", value: "NOT_CONTACTED" },
  { label: "Contacted", value: "CONTACTED" },
  { label: "Responded", value: "RESPONDED" },
  { label: "Interested", value: "INTERESTED" },
  { label: "Declined", value: "DECLINED" },
  { label: "Bounced", value: "BOUNCED" },
];

const TYPE_OPTIONS: { label: string; value: CompanyType | "" }[] = [
  { label: "All types", value: "" },
  { label: "Target", value: "TARGET" },
  { label: "Buyer", value: "BUYER" },
  { label: "Investor", value: "INVESTOR" },
];

function cadenceLabel(company: Company): React.ReactNode {
  if (!company.schedule_status) return null;
  const state = cadenceStateFromSchedule({
    scheduleStatus: company.schedule_status,
    daysRemaining: company.days_remaining,
  });
  let label: string | undefined;
  if (state === "overdue") label = `${Math.abs(company.days_remaining!)}d overdue`;
  else if (state === "due_soon") label = `due in ${company.days_remaining}d`;
  return <CadenceBadge state={state} label={label} />;
}

const COLUMNS: Column<Company>[] = [
  {
    key: "company_name",
    header: "Company",
    cell: (row) => (
      <div className="flex items-center gap-2 min-w-0">
        <span
          className={`h-2 w-2 flex-shrink-0 rounded-full ${SOURCE_DOT[row.source] ?? "bg-gray-400"}`}
          title={row.source}
        />
        <span className="font-medium truncate max-w-[200px]">{row.company_name}</span>
      </div>
    ),
    className: "w-[220px]",
  },
  {
    key: "type_bucket",
    header: "Type / Bucket",
    cell: (row) => (
      <div className="flex flex-col gap-0.5">
        <span className="text-xs text-muted-foreground">{row.type}</span>
        {row.bucket && (
          <Badge variant="outline" className="text-[10px] px-1 py-0 h-4 w-fit">
            {row.bucket}
          </Badge>
        )}
      </div>
    ),
    className: "w-[120px]",
  },
  {
    key: "status",
    header: "Status",
    cell: (row) => <StatusBadge status={row.status} />,
    className: "w-[130px]",
  },
  {
    key: "cadence",
    header: "Schedule",
    cell: (row) => cadenceLabel(row),
    className: "w-[150px]",
  },
  {
    key: "primary_contact",
    header: "Primary Contact",
    cell: (row) =>
      row.primary_contact ? (
        <div className="flex flex-col gap-0.5 min-w-0">
          <span className="text-sm font-medium truncate">{row.primary_contact.contact_person}</span>
          {row.primary_contact.designation && (
            <span className="text-xs text-muted-foreground truncate">
              {row.primary_contact.designation}
            </span>
          )}
        </div>
      ) : (
        <span className="text-xs text-muted-foreground">—</span>
      ),
    className: "w-[180px]",
  },
  {
    key: "hq",
    header: "HQ",
    cell: (row) => (
      <span className="text-sm text-muted-foreground">{row.hq ?? "—"}</span>
    ),
    className: "w-[100px]",
  },
];

export default function CompaniesPage() {
  const router = useRouter();
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<CompanyStatus | "">("");
  const [type, setType] = useState<CompanyType | "">("");
  const [includeArchived, setIncludeArchived] = useState(false);
  const [page, setPage] = useState(1);
  // Honor a ?mandate_id= deep-link (e.g. from a mandate detail page). Read after mount
  // (not in a useState initializer) so server and client first render match — avoids a
  // hydration mismatch on /companies?mandate_id=X.
  const [mandateId, setMandateId] = useState<number | undefined>(undefined);
  useEffect(() => {
    const v = new URLSearchParams(window.location.search).get("mandate_id");
    if (v) setMandateId(Number(v));
  }, []);

  const filters: CompanyFilters = {
    q: search || undefined,
    status: status || undefined,
    type: type || undefined,
    mandate_id: mandateId,
    include_archived: includeArchived || undefined,
    page,
    page_size: PAGE_SIZE,
  };

  const { data, isLoading, error } = useCompanies(filters);

  const summary = data?.summary;
  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 1;

  return (
    <div className="flex flex-col gap-6 p-6">
      <PageHeader
        title="Master List"
        description="All target companies across mandates."
        actions={<CompanyDialog defaultMandateId={mandateId} />}
      />

      {/* Summary stat strip */}
      {summary && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <StatCard
            label="Total"
            value={String(data?.total ?? 0)}
          />
          <StatCard
            label="Needs first outreach"
            value={String(summary.needs_initial_count)}
            className="text-violet-600"
          />
          <StatCard
            label="Overdue"
            value={String(summary.overdue_count)}
            className={summary.overdue_count > 0 ? "text-red-600" : undefined}
          />
          <StatCard
            label="Responded"
            value={`${Math.round(summary.responded_pct * 100)}%`}
            className="text-green-600"
          />
        </div>
      )}

      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-2">
        <div className="relative flex-1 min-w-[180px] max-w-xs">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search companies..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="pl-8"
          />
        </div>

        <select
          value={status}
          onChange={(e) => { setStatus(e.target.value as CompanyStatus | ""); setPage(1); }}
          className="h-9 rounded-md border border-input bg-background px-3 text-sm"
        >
          {STATUS_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>

        <select
          value={type}
          onChange={(e) => { setType(e.target.value as CompanyType | ""); setPage(1); }}
          className="h-9 rounded-md border border-input bg-background px-3 text-sm"
        >
          {TYPE_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>

        <label className="flex items-center gap-1.5 text-sm text-muted-foreground cursor-pointer">
          <input
            type="checkbox"
            checked={includeArchived}
            onChange={(e) => { setIncludeArchived(e.target.checked); setPage(1); }}
            className="h-3.5 w-3.5 rounded"
          />
          Show archived
        </label>

        {mandateId && (
          <button
            onClick={() => router.push("/companies")}
            className="inline-flex items-center gap-1 rounded-full bg-muted px-2.5 py-1 text-xs text-muted-foreground hover:text-foreground"
          >
            Mandate #{mandateId}
            <span aria-hidden>×</span>
          </button>
        )}
      </div>

      {/* Table */}
      <DataTable
        columns={COLUMNS}
        data={data?.items}
        getRowId={(row) => row.id}
        isLoading={isLoading}
        error={error}
        onRowClick={(row) => router.push(`/companies/${row.id}`)}
        emptyState={
          <EmptyState
            icon={Building2}
            title="No companies"
            description={search || status || type ? "Try adjusting your filters." : "Add the first company to this mandate."}
          />
        }
      />

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">
            {data?.total} companies
          </span>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              Previous
            </Button>
            <span className="flex items-center px-2 text-muted-foreground">
              {page} / {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
