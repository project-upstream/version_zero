"use client";

import Link from "next/link";
import {
  Building2,
  CalendarClock,
  CheckCircle2,
  Send,
  AlertTriangle,
} from "lucide-react";
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import { useAnalyticsOverview, useResponseByBucket } from "@/hooks/use-analytics";
import { useDue } from "@/hooks/use-schedule";
import { useAuth } from "@/hooks/use-auth";
import { StatCard } from "@/components/features/stat-card";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/features/status-badge";
import type { CompanyStatus } from "@/types";

const STATUS_COLORS: Record<string, string> = {
  RESPONDED:     "#4ade80",   // chart-2 emerald
  INTERESTED:    "#818cf8",   // chart-3 indigo
  CONTACTED:     "#64748b",
  NOT_CONTACTED: "#334155",
  DECLINED:      "#c47d08",   // chart-1 amber
  BOUNCED:       "#f87171",   // chart-5 red
};

function greeting() {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 17) return "Good afternoon";
  return "Good evening";
}

export default function DashboardPage() {
  const { data: overview, isLoading: ovLoading } = useAnalyticsOverview();
  const { data: buckets } = useResponseByBucket();
  const { data: due } = useDue(7);
  const { user } = useAuth();

  const firstName = user?.full_name?.split(" ")[0] ?? "";

  const donutData = overview
    ? Object.entries(overview.by_status).map(([name, value]) => ({ name, value }))
    : [];

  const barData =
    buckets?.items.slice(0, 8).map((b) => ({
      bucket: b.bucket.length > 14 ? b.bucket.slice(0, 14) + "…" : b.bucket,
      rate: Math.round(b.response_rate * 100),
    })) ?? [];

  const hasOverdue = (overview?.overdue ?? 0) > 0;

  return (
    <div className="flex flex-col gap-6 p-6">
      <PageHeader
        title="Dashboard"
        description={firstName ? `${greeting()}, ${firstName}.` : undefined}
      />

      {/* KPI strip — staggered entrance */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-5">
        {[
          {
            label: "Total companies",
            value: overview?.total ?? null,
            icon: Building2,
          },
          {
            label: "Responded",
            value: overview ? Math.round(overview.responded_pct * 100) : null,
            icon: CheckCircle2,
            isPercent: true,
          },
          {
            label: "Needs first outreach",
            value: overview?.needs_initial ?? null,
            icon: Send,
          },
          {
            label: "Due this week",
            value: overview?.due_this_week ?? null,
            icon: CalendarClock,
          },
          {
            label: "Overdue",
            value: overview?.overdue ?? null,
            icon: AlertTriangle,
            isOverdue: true,
          },
        ].map((card, i) => (
          <StatCard
            key={card.label}
            label={card.label}
            value={card.value}
            icon={card.icon}
            isLoading={ovLoading}
            isPercent={card.isPercent}
            className={
              card.isOverdue && hasOverdue
                ? "stat-card-overdue stat-card-overdue-active"
                : undefined
            }
            style={{ animationDelay: `${i * 65}ms` }}
          />
        ))}
      </div>

      {/* Charts row */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Status mix donut */}
        <Card>
          <CardHeader>
            <CardTitle className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
              Status mix
            </CardTitle>
          </CardHeader>
          <CardContent>
            {donutData.length === 0 ? (
              <p className="py-8 text-center text-sm text-muted-foreground">No data</p>
            ) : (
              <div className="flex items-center gap-6">
                <ResponsiveContainer width={140} height={140}>
                  <PieChart>
                    <Pie
                      data={donutData}
                      cx="50%"
                      cy="50%"
                      innerRadius={40}
                      outerRadius={65}
                      dataKey="value"
                      strokeWidth={0}
                    >
                      {donutData.map((entry) => (
                        <Cell
                          key={entry.name}
                          fill={STATUS_COLORS[entry.name] ?? "oklch(0.35 0.008 265)"}
                        />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
                <ul className="flex flex-col gap-1.5 text-xs">
                  {donutData.map((d) => (
                    <li key={d.name} className="flex items-center gap-2">
                      <span
                        className="inline-block h-2 w-2 shrink-0 rounded-full"
                        style={{ backgroundColor: STATUS_COLORS[d.name] ?? "oklch(0.35 0.008 265)" }}
                      />
                      <span className="text-muted-foreground capitalize">
                        {d.name.toLowerCase().replace("_", " ")}
                      </span>
                      <span className="ml-auto font-mono font-medium tabular-nums">{d.value}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Response-by-bucket bar */}
        <Card>
          <CardHeader>
            <CardTitle className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
              Response rate by bucket
            </CardTitle>
          </CardHeader>
          <CardContent>
            {barData.length === 0 ? (
              <p className="py-8 text-center text-sm text-muted-foreground">No data</p>
            ) : (
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={barData} margin={{ top: 0, right: 0, bottom: 0, left: -20 }}>
                  <XAxis
                    dataKey="bucket"
                    tick={{ fontSize: 11, fill: "var(--muted-foreground)" }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fontSize: 11, fill: "var(--muted-foreground)" }}
                    axisLine={false}
                    tickLine={false}
                    unit="%"
                  />
                  <Tooltip
                    formatter={(v) => [`${v}%`, "Response rate"]}
                    contentStyle={{
                      fontSize: 12,
                      background: "var(--popover)",
                      border: "1px solid var(--border)",
                      borderRadius: "var(--radius)",
                      color: "var(--foreground)",
                    }}
                    cursor={{ fill: "oklch(0.72 0.16 58 / 0.06)" }}
                  />
                  <Bar dataKey="rate" fill="#c47d08" radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Due this week mini-list */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
              Due this week
            </CardTitle>
            <Link href="/schedule" className="text-xs text-primary hover:underline">
              View all →
            </Link>
          </div>
        </CardHeader>
        <CardContent>
          {!due || due.items.length === 0 ? (
            <p className="py-4 text-center text-sm text-muted-foreground">All clear this week</p>
          ) : (
            <ul className="divide-y divide-border/50">
              {due.items.slice(0, 8).map((item) => (
                <li
                  key={item.company_id}
                  className="flex items-center justify-between py-2 hover:bg-primary/[0.04] transition-colors"
                >
                  <Link
                    href={`/companies/${item.company_id}`}
                    className="text-sm font-medium hover:underline"
                  >
                    {item.company_name}
                  </Link>
                  <div className="flex items-center gap-3 text-xs text-muted-foreground">
                    <StatusBadge status={item.company_status as CompanyStatus} />
                    <span
                      className={cn(
                        "font-mono tabular-nums",
                        item.days_remaining != null && item.days_remaining < 0
                          ? "text-destructive font-medium"
                          : "",
                      )}
                    >
                      {item.days_remaining != null && item.days_remaining < 0
                        ? `${Math.abs(item.days_remaining)}d overdue`
                        : item.days_remaining != null
                        ? `in ${item.days_remaining}d`
                        : "—"}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function cn(...classes: (string | undefined | null | false)[]) {
  return classes.filter(Boolean).join(" ");
}
