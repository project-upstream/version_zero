"use client";

import { use, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Archive, ArchiveRestore, UserPlus, X } from "lucide-react";
import { toast } from "sonner";

import {
  useMandate,
  useMandateCompanies,
  useArchiveMandate,
  useAssignUser,
  useUnassignUser,
} from "@/hooks/use-mandates";
import { useUsers } from "@/hooks/use-users";
import { useAuth } from "@/hooks/use-auth";
import { MandateDialog } from "@/components/features/mandate-dialog";
import { StatusBadge } from "@/components/features/status-badge";
import { StatCard } from "@/components/features/stat-card";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { CompanyStatus } from "@/types";

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

function AssignmentsCard({ mandateId }: { mandateId: number }) {
  const { data: mandate } = useMandate(mandateId);
  const { data: users } = useUsers();
  const { user } = useAuth();
  const assign = useAssignUser();
  const unassign = useUnassignUser();
  const [selected, setSelected] = useState("");

  const isPartner = user?.role === "PARTNER";
  const assigned = mandate?.assignments ?? [];
  const assignedIds = new Set(assigned.map((a) => a.id));
  const assignable = (users?.items ?? []).filter((u) => !assignedIds.has(u.id));

  const handleAssign = async () => {
    if (!selected) return;
    try {
      await assign.mutateAsync({ mandateId, userId: Number(selected) });
      toast.success("Analyst assigned");
      setSelected("");
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : "Failed to assign");
    }
  };

  return (
    <Card>
      <CardHeader><CardTitle className="text-sm">Team ({assigned.length})</CardTitle></CardHeader>
      <CardContent className="space-y-3">
        {assigned.length === 0 ? (
          <p className="text-sm text-muted-foreground">No one assigned yet.</p>
        ) : (
          <ul className="space-y-2">
            {assigned.map((a) => (
              <li key={a.id} className="flex items-center justify-between text-sm">
                <div>
                  <span className="font-medium">{a.full_name}</span>
                  <span className="ml-2 text-xs text-muted-foreground capitalize">
                    {a.role.toLowerCase()}
                  </span>
                </div>
                {isPartner && (
                  <button
                    onClick={async () => {
                      try {
                        await unassign.mutateAsync({ mandateId, userId: a.id });
                        toast.success("Removed");
                      } catch {
                        toast.error("Failed to remove");
                      }
                    }}
                    className="text-muted-foreground hover:text-destructive"
                    aria-label={`Remove ${a.full_name}`}
                  >
                    <X className="h-4 w-4" />
                  </button>
                )}
              </li>
            ))}
          </ul>
        )}

        {isPartner && assignable.length > 0 && (
          <div className="flex gap-2 pt-2 border-t">
            <select
              value={selected}
              onChange={(e) => setSelected(e.target.value)}
              className="h-9 flex-1 rounded-md border border-input bg-background px-3 text-sm"
            >
              <option value="">Assign someone…</option>
              {assignable.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.full_name} ({u.role.toLowerCase()})
                </option>
              ))}
            </select>
            <Button size="sm" onClick={handleAssign} disabled={!selected || assign.isPending}>
              <UserPlus className="mr-1 h-4 w-4" />
              Assign
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default function MandateDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const mandateId = Number(id);
  const router = useRouter();
  const { user } = useAuth();
  const { data: mandate, isLoading, error } = useMandate(mandateId);
  const { data: companies } = useMandateCompanies(mandateId);
  const archive = useArchiveMandate();

  const isPartner = user?.role === "PARTNER";

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="h-8 w-48 animate-pulse rounded-md bg-muted mb-4" />
        <div className="h-4 w-64 animate-pulse rounded-md bg-muted" />
      </div>
    );
  }

  if (error || !mandate) {
    return (
      <div className="p-6">
        <p className="text-sm text-muted-foreground">Mandate not found.</p>
      </div>
    );
  }

  const isArchived = !!mandate.archived_at;

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Back + actions */}
      <div className="flex items-center justify-between">
        <Button variant="ghost" size="sm" onClick={() => router.back()}>
          <ArrowLeft className="mr-1 h-4 w-4" />
          Back
        </Button>
        {isPartner && (
          <div className="flex gap-2">
            <MandateDialog
              mandate={mandate}
              trigger={<Button variant="outline" size="sm">Edit</Button>}
            />
            <Button
              variant="outline"
              size="sm"
              onClick={async () => {
                const verb = isArchived ? "restore" : "archive";
                if (!confirm(`${isArchived ? "Restore" : "Archive"} this mandate? Data is ${isArchived ? "made active again" : "kept, not destroyed"}.`)) return;
                try {
                  await archive.mutateAsync({ id: mandate.id, archived: isArchived });
                  toast.success(`Mandate ${verb}d`);
                } catch {
                  toast.error(`Failed to ${verb} mandate`);
                }
              }}
            >
              {isArchived ? (
                <><ArchiveRestore className="mr-1 h-4 w-4" /> Restore</>
              ) : (
                <><Archive className="mr-1 h-4 w-4" /> Archive</>
              )}
            </Button>
          </div>
        )}
      </div>

      {/* Header */}
      <div className="flex flex-wrap items-start gap-3">
        <div className="flex-1 min-w-0">
          <PageHeader title={mandate.name} description={mandate.client_name} />
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {isArchived && <Badge variant="secondary">Archived</Badge>}
          <span className="text-sm text-muted-foreground">{TYPE_LABELS[mandate.type]}</span>
          <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_STYLE[mandate.status] ?? ""}`}>
            {mandate.status.replace("_", " ").toLowerCase()}
          </span>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatCard label="Companies" value={mandate.stats.total} />
        <StatCard label="Responded" value={`${Math.round(mandate.stats.responded_pct * 100)}%`} />
        <StatCard label="Needs outreach" value={mandate.stats.needs_initial} />
        <StatCard label="Lead owner" value={mandate.lead_owner?.full_name ?? "—"} />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Companies (mini) */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm">Companies ({companies?.total ?? 0})</CardTitle>
              <Link
                href={`/companies?mandate_id=${mandate.id}`}
                className="text-xs text-primary hover:underline"
              >
                View in Master List →
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            {!companies || companies.items.length === 0 ? (
              <p className="py-4 text-center text-sm text-muted-foreground">
                No companies in this mandate yet.
              </p>
            ) : (
              <ul className="divide-y">
                {companies.items.slice(0, 12).map((c) => (
                  <li key={c.id} className="flex items-center justify-between py-2">
                    <Link
                      href={`/companies/${c.id}`}
                      className="text-sm font-medium hover:underline truncate"
                    >
                      {c.company_name}
                    </Link>
                    <StatusBadge status={c.status as CompanyStatus} />
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        {/* Team / assignments */}
        <AssignmentsCard mandateId={mandate.id} />
      </div>
    </div>
  );
}
