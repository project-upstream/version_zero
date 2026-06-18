"use client";

import { useRouter } from "next/navigation";
import { CalendarClock, Mail, AlertTriangle, Clock } from "lucide-react";

import {
  useNeedsInitial,
  useDue,
  useScheduleStats,
  type ScheduleRow,
} from "@/hooks/use-schedule";
import { StatCard } from "@/components/features/stat-card";
import { EmptyState } from "@/components/features/empty-state";
import { LogOutreachDialog } from "@/components/features/log-outreach-dialog";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { TableSkeleton } from "@/components/features/table-skeleton";
import { cn } from "@/lib/utils";

function QueueRow({ row }: { row: ScheduleRow }) {
  const router = useRouter();
  const isOverdue = row.is_overdue;
  const daysLabel =
    row.days_remaining === null
      ? null
      : row.days_remaining < 0
      ? `${Math.abs(row.days_remaining)}d overdue`
      : row.days_remaining === 0
      ? "due today"
      : `due in ${row.days_remaining}d`;

  return (
    <div className="flex items-center justify-between gap-4 py-3 transition-colors hover:bg-primary/[0.04]">
      <div className="flex-1 min-w-0">
        <button
          onClick={() => router.push(`/companies/${row.company_id}`)}
          className="text-sm font-medium hover:underline text-left truncate max-w-[200px]"
        >
          {row.company_name}
        </button>
        <div className="flex items-center gap-2 mt-0.5 flex-wrap">
          {daysLabel && (
            <span
              className={cn(
                "text-xs font-mono tabular-nums",
                isOverdue ? "text-destructive font-medium" : "text-muted-foreground",
              )}
            >
              {daysLabel}
            </span>
          )}
          {row.regarding && (
            <span className="text-xs text-muted-foreground truncate">{row.regarding}</span>
          )}
          {row.last_event_date && (
            <span className="text-xs text-muted-foreground font-mono">
              last: {row.last_event_date}
            </span>
          )}
        </div>
      </div>
      <LogOutreachDialog
        companyId={row.company_id}
        companyName={row.company_name}
        defaultEventType={row.schedule_status === "AWAITING_INITIAL" ? "INITIAL_EMAIL" : "FOLLOW_UP"}
        trigger={
          <Button size="sm" variant={isOverdue ? "destructive" : "outline"}>
            Log outreach
          </Button>
        }
      />
    </div>
  );
}

function Section({
  title,
  rows,
  isLoading,
  icon: Icon,
  emptyText,
  urgent,
}: {
  title: string;
  rows: ScheduleRow[];
  isLoading?: boolean;
  icon: React.ElementType;
  emptyText: string;
  urgent?: boolean;
}) {
  return (
    <div
      className={cn(
        "rounded-lg p-4",
        urgent ? "border border-primary/20" : "",
      )}
      style={urgent ? { background: "oklch(0.72 0.16 58 / 0.05)" } : undefined}
    >
      <div className="flex items-center gap-2 mb-3">
        <Icon
          className={cn("h-4 w-4", urgent ? "text-primary" : "text-muted-foreground")}
        />
        <h2
          className={cn(
            "text-[11px] font-semibold uppercase tracking-widest",
            urgent ? "text-primary" : "text-muted-foreground",
          )}
        >
          {title}
        </h2>
        {!isLoading && (
          <span
            className={cn(
              "ml-1 rounded-full px-1.5 py-0.5 text-[10px] font-medium",
              urgent
                ? "bg-primary/20 text-primary"
                : "bg-muted text-muted-foreground",
            )}
          >
            {rows.length}
          </span>
        )}
      </div>
      {isLoading ? (
        <TableSkeleton cols={2} rows={3} />
      ) : rows.length === 0 ? (
        <p className="text-xs text-muted-foreground py-2">{emptyText}</p>
      ) : (
        <div className="divide-y divide-border/40 rounded-lg border overflow-hidden px-4">
          {rows.map((r) => (
            <QueueRow key={r.company_id} row={r} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function SchedulePage() {
  const { data: needsInitial, isLoading: loadingNI } = useNeedsInitial();
  const { data: due, isLoading: loadingDue } = useDue(7);
  const { data: stats, isLoading: loadingStats } = useScheduleStats();

  const dueItems = due?.items ?? [];
  const overdue = dueItems.filter((r) => r.is_overdue);
  const dueToday = dueItems.filter((r) => !r.is_overdue && r.days_remaining === 0);
  const dueThisWeek = dueItems.filter(
    (r) => !r.is_overdue && r.days_remaining !== null && r.days_remaining > 0,
  );

  const overdueCount = stats?.overdue_count ?? null;
  const hasOverdue = (overdueCount ?? 0) > 0;

  return (
    <div className="flex flex-col gap-6 p-6">
      <PageHeader title="Email Schedule" description="Your outreach work queue." />

      {/* Stats strip */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatCard
          label="Sent this week"
          value={loadingStats ? null : (stats?.sent_this_week ?? 0)}
        />
        <StatCard
          label="Responses this week"
          value={loadingStats ? null : (stats?.responses_this_week ?? 0)}
        />
        <StatCard
          label="Response rate"
          value={loadingStats ? null : Math.round((stats?.response_rate ?? 0) * 100)}
          isPercent
        />
        <StatCard
          label="Overdue"
          value={loadingStats ? null : overdueCount}
          className={hasOverdue ? "stat-card-overdue stat-card-overdue-active" : undefined}
        />
      </div>

      {/* Overdue — highest priority, amber-tinted, shown first */}
      {(overdue.length > 0 || loadingDue) && (
        <Section
          title="Overdue"
          rows={overdue}
          isLoading={loadingDue}
          icon={AlertTriangle}
          emptyText="No overdue follow-ups."
          urgent
        />
      )}

      {/* Due today */}
      {(dueToday.length > 0 || loadingDue) && (
        <Section
          title="Due today"
          rows={dueToday}
          isLoading={loadingDue}
          icon={Clock}
          emptyText=""
        />
      )}

      {/* Due this week */}
      <Section
        title="Due this week"
        rows={dueThisWeek}
        isLoading={loadingDue}
        icon={Mail}
        emptyText="No follow-ups due this week."
      />

      {/* Needs first outreach — below the fold, informational */}
      <Section
        title="Needs first outreach"
        rows={needsInitial?.items ?? []}
        isLoading={loadingNI}
        icon={CalendarClock}
        emptyText="No companies awaiting initial outreach."
      />
    </div>
  );
}
