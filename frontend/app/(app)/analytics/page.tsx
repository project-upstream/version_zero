"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import { useResponseByBucket, useByAnalyst, useSources } from "@/hooks/use-analytics";
import { useAuth } from "@/hooks/use-auth";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

function pct(rate: number) {
  return `${Math.round(rate * 100)}%`;
}

const TOOLTIP_STYLE = {
  fontSize: 12,
  background: "var(--popover)",
  border: "1px solid var(--border)",
  borderRadius: "var(--radius)",
  color: "var(--foreground)",
};

export default function AnalyticsPage() {
  const { user } = useAuth();
  const { data: buckets, isLoading: bucketsLoading } = useResponseByBucket();
  const { data: analysts } = useByAnalyst();
  const { data: sources } = useSources();

  const isPartner = user?.role === "PARTNER";

  const barData =
    buckets?.items.map((b) => ({
      bucket: b.bucket.length > 16 ? b.bucket.slice(0, 16) + "…" : b.bucket,
      rate: Math.round(b.response_rate * 100),
      total: b.total,
    })) ?? [];

  return (
    <div className="flex flex-col gap-6 p-6">
      <PageHeader title="Analytics" />

      {/* Response rate by bucket */}
      <Card>
        <CardHeader>
          <CardTitle className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
            Response rate by bucket
          </CardTitle>
        </CardHeader>
        <CardContent>
          {bucketsLoading ? (
            <div className="h-48 animate-pulse rounded-md bg-muted" />
          ) : barData.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">No bucket data</p>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={barData} margin={{ top: 0, right: 0, bottom: 24, left: -20 }}>
                <XAxis
                  dataKey="bucket"
                  tick={{ fontSize: 11, fill: "var(--muted-foreground)" }}
                  angle={-20}
                  textAnchor="end"
                  interval={0}
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
                  formatter={(v, _name, props) => [
                    `${v}% (${(props as { payload?: { total?: number } })?.payload?.total ?? ""} total)`,
                    "Response rate",
                  ]}
                  contentStyle={TOOLTIP_STYLE}
                  cursor={{ fill: "oklch(0.72 0.16 58 / 0.06)" }}
                />
                <Bar dataKey="rate" fill="#c47d08" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      {/* Source quality panel */}
      <Card>
        <CardHeader>
          <CardTitle className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
            Source quality
          </CardTitle>
        </CardHeader>
        <CardContent>
          {!sources || sources.items.length === 0 ? (
            <p className="py-4 text-center text-sm text-muted-foreground">No source data</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="pb-2 text-left text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">Source</th>
                    <th className="pb-2 text-left text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">Quality</th>
                    <th className="pb-2 text-right text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">Total</th>
                    <th className="pb-2 text-right text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">Responded</th>
                    <th className="pb-2 text-right text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">Rate</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/40">
                  {sources.items.map((row, i) => (
                    <tr key={i} className="text-sm hover:bg-primary/[0.04] transition-colors">
                      <td className="py-2">{row.source ?? "—"}</td>
                      <td className="py-2">{row.source_quality ?? "—"}</td>
                      <td className="py-2 text-right font-mono tabular-nums">{row.total}</td>
                      <td className="py-2 text-right font-mono tabular-nums">{row.responded}</td>
                      <td className="py-2 text-right font-mono tabular-nums font-medium text-primary">
                        {pct(row.response_rate)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* By-analyst table — partner only (A-02) */}
      {isPartner && (
        <Card>
          <CardHeader>
            <CardTitle className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
              Analyst performance
            </CardTitle>
          </CardHeader>
          <CardContent>
            {!analysts || analysts.items.length === 0 ? (
              <p className="py-4 text-center text-sm text-muted-foreground">No analyst data</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="pb-2 text-left text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">Name</th>
                      <th className="pb-2 text-left text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">Role</th>
                      <th className="pb-2 text-right text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">Events</th>
                      <th className="pb-2 text-right text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">Initial</th>
                      <th className="pb-2 text-right text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">Responses</th>
                      <th className="pb-2 text-right text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">Conversion</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/40">
                    {analysts.items.map((row) => (
                      <tr key={row.user_id} className="hover:bg-primary/[0.04] transition-colors">
                        <td className="py-2 font-medium">{row.full_name}</td>
                        <td className="py-2 text-muted-foreground capitalize">
                          {row.role.toLowerCase()}
                        </td>
                        <td className="py-2 text-right font-mono tabular-nums">{row.total_events}</td>
                        <td className="py-2 text-right font-mono tabular-nums">{row.initial_emails}</td>
                        <td className="py-2 text-right font-mono tabular-nums">{row.responses}</td>
                        <td className="py-2 text-right font-mono tabular-nums font-medium text-primary">
                          {pct(row.conversion_rate)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
