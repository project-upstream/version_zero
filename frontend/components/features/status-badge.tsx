import { cn } from "@/lib/utils";
import type { CompanyStatus } from "@/types";

const PILL_BASE =
  "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset ring-black/[0.06] dark:ring-white/5 whitespace-nowrap";

const STATUS_CONFIG: Record<CompanyStatus, { label: string; className: string }> = {
  NOT_CONTACTED: {
    label: "Not contacted",
    className:
      "[background:oklch(0.93_0.004_265)] [color:oklch(0.44_0.02_265)] dark:[background:oklch(0.25_0.01_265_/_0.6)] dark:[color:oklch(0.55_0.01_265)]",
  },
  CONTACTED: {
    label: "Contacted",
    className:
      "[background:oklch(0.92_0.015_250)] [color:oklch(0.42_0.04_255)] dark:[background:oklch(0.30_0.02_265_/_0.6)] dark:[color:oklch(0.72_0.02_265)]",
  },
  RESPONDED: {
    label: "Responded",
    className:
      "[background:oklch(0.93_0.05_152)] [color:oklch(0.46_0.13_152)] dark:[background:oklch(0.20_0.10_152_/_0.6)] dark:[color:oklch(0.72_0.18_152)]",
  },
  INTERESTED: {
    label: "Interested",
    className:
      "[background:oklch(0.93_0.045_270)] [color:oklch(0.48_0.15_270)] dark:[background:oklch(0.20_0.12_270_/_0.6)] dark:[color:oklch(0.72_0.18_270)]",
  },
  DECLINED: {
    label: "Declined",
    className:
      "[background:oklch(0.94_0.05_75)] [color:oklch(0.52_0.12_60)] dark:[background:oklch(0.22_0.08_58_/_0.6)] dark:[color:oklch(0.78_0.16_58)]",
  },
  BOUNCED: {
    label: "Bounced",
    className:
      "[background:oklch(0.93_0.05_25)] [color:oklch(0.52_0.20_25)] dark:[background:oklch(0.22_0.12_25_/_0.6)] dark:[color:oklch(0.72_0.22_25)]",
  },
};

export function StatusBadge({
  status,
  className,
}: {
  status: CompanyStatus;
  className?: string;
}) {
  const cfg = STATUS_CONFIG[status];
  return <span className={cn(PILL_BASE, cfg.className, className)}>{cfg.label}</span>;
}

export type CadenceState =
  | "needs_initial"
  | "overdue"
  | "due_soon"
  | "upcoming"
  | "stopped";

const CADENCE_CONFIG: Record<CadenceState, { label: string; className: string }> = {
  needs_initial: {
    label: "Needs first outreach",
    className:
      "[background:oklch(0.93_0.045_270)] [color:oklch(0.48_0.15_270)] dark:[background:oklch(0.20_0.12_270_/_0.6)] dark:[color:oklch(0.72_0.18_270)]",
  },
  overdue: {
    label: "Overdue",
    className:
      "[background:oklch(0.93_0.05_25)] [color:oklch(0.52_0.20_25)] dark:[background:oklch(0.22_0.12_25_/_0.6)] dark:[color:oklch(0.72_0.22_25)]",
  },
  due_soon: {
    label: "Due soon",
    className:
      "[background:oklch(0.94_0.05_75)] [color:oklch(0.52_0.12_60)] dark:[background:oklch(0.22_0.08_58_/_0.6)] dark:[color:oklch(0.78_0.16_58)]",
  },
  upcoming: {
    label: "Upcoming",
    className:
      "[background:oklch(0.92_0.015_250)] [color:oklch(0.42_0.04_255)] dark:[background:oklch(0.30_0.02_265_/_0.6)] dark:[color:oklch(0.72_0.02_265)]",
  },
  stopped: {
    label: "Stopped",
    className:
      "[background:oklch(0.93_0.004_265)] [color:oklch(0.44_0.02_265)] dark:[background:oklch(0.25_0.01_265_/_0.6)] dark:[color:oklch(0.55_0.01_265)]",
  },
};

export function CadenceBadge({
  state,
  label,
  className,
}: {
  state: CadenceState;
  label?: string;
  className?: string;
}) {
  const cfg = CADENCE_CONFIG[state];
  return (
    <span className={cn(PILL_BASE, cfg.className, className)}>{label ?? cfg.label}</span>
  );
}

export function cadenceStateFromSchedule(args: {
  scheduleStatus: "AWAITING_INITIAL" | "ACTIVE" | "STOPPED";
  daysRemaining: number | null;
  window?: number;
}): CadenceState {
  const { scheduleStatus, daysRemaining, window = 7 } = args;
  if (scheduleStatus === "AWAITING_INITIAL") return "needs_initial";
  if (scheduleStatus === "STOPPED") return "stopped";
  if (daysRemaining === null) return "upcoming";
  if (daysRemaining < 0) return "overdue";
  if (daysRemaining <= window) return "due_soon";
  return "upcoming";
}
