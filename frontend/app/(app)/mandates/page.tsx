"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Briefcase } from "lucide-react";

import { useMandates } from "@/hooks/use-mandates";
import { useAuth } from "@/hooks/use-auth";
import { MandateDialog } from "@/components/features/mandate-dialog";
import { DataTable, type Column } from "@/components/features/data-table";
import { EmptyState } from "@/components/features/empty-state";
import { PageHeader } from "@/components/layout/page-header";
import { Badge } from "@/components/ui/badge";
import type { MandateListItem } from "@/types";

const TYPE_LABELS: Record<string, string> = {
  SELL_SIDE: "Sell-side",
  BUY_SIDE: "Buy-side",
  CAPITAL_RAISE: "Capital raise",
};

const STATUS_STYLE: Record<string, string> = {
  ACTIVE: "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300",
  ON_HOLD: "bg-amber-100 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300",
  CLOSED: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300",
  TERMINATED: "bg-red-100 text-red-700 dark:bg-red-950/40 dark:text-red-300",
};

function MandateStatusBadge({ status }: { status: string }) {
  return (
    <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_STYLE[status] ?? ""}`}>
      {status.replace("_", " ").toLowerCase()}
    </span>
  );
}

const COLUMNS: Column<MandateListItem>[] = [
  {
    key: "name",
    header: "Mandate",
    cell: (row) => (
      <div className="flex flex-col gap-0.5 min-w-0">
        <span className="font-medium truncate">{row.name}</span>
        <span className="text-xs text-muted-foreground truncate">{row.client_name}</span>
      </div>
    ),
    className: "w-[240px]",
  },
  {
    key: "type",
    header: "Type",
    cell: (row) => <span className="text-sm text-muted-foreground">{TYPE_LABELS[row.type] ?? row.type}</span>,
    className: "w-[120px]",
  },
  {
    key: "status",
    header: "Status",
    cell: (row) => <MandateStatusBadge status={row.status} />,
    className: "w-[120px]",
  },
  {
    key: "companies",
    header: "Companies",
    cell: (row) => <span className="text-sm tabular-nums">{row.total}</span>,
    className: "w-[100px]",
  },
  {
    key: "responded",
    header: "Responded",
    cell: (row) => (
      <span className="text-sm tabular-nums">{Math.round(row.responded_pct * 100)}%</span>
    ),
    className: "w-[100px]",
  },
  {
    key: "needs_initial",
    header: "Needs outreach",
    cell: (row) =>
      row.needs_initial > 0 ? (
        <Badge variant="outline" className="text-violet-600">{row.needs_initial}</Badge>
      ) : (
        <span className="text-xs text-muted-foreground">—</span>
      ),
    className: "w-[120px]",
  },
];

export default function MandatesPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [includeArchived, setIncludeArchived] = useState(false);
  const { data, isLoading, error } = useMandates(includeArchived);

  const isPartner = user?.role === "PARTNER";

  return (
    <div className="flex flex-col gap-6 p-6">
      <PageHeader
        title="Mandates"
        description="Deals and engagements across the firm."
        actions={isPartner ? <MandateDialog /> : undefined}
      />

      <div className="flex items-center gap-2">
        <label className="flex items-center gap-1.5 text-sm text-muted-foreground cursor-pointer">
          <input
            type="checkbox"
            checked={includeArchived}
            onChange={(e) => setIncludeArchived(e.target.checked)}
            className="h-3.5 w-3.5 rounded"
          />
          Show archived
        </label>
      </div>

      <DataTable
        columns={COLUMNS}
        data={data?.items}
        getRowId={(row) => row.id}
        isLoading={isLoading}
        error={error}
        onRowClick={(row) => router.push(`/mandates/${row.id}`)}
        emptyState={
          <EmptyState
            icon={Briefcase}
            title="No mandates"
            description={isPartner ? "Create the first mandate to get started." : "You have no assigned mandates yet."}
          />
        }
      />
    </div>
  );
}
