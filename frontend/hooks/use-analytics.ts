"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export interface OverviewStats {
  total: number;
  by_status: Record<string, number>;
  responded_pct: number;
  due_this_week: number;
  overdue: number;
  needs_initial: number;
  active_mandates: number;
}

export interface BucketRow {
  bucket: string;
  total: number;
  responded: number;
  response_rate: number;
}

export interface AnalystRow {
  user_id: number;
  full_name: string;
  role: string;
  total_events: number;
  initial_emails: number;
  responses: number;
  conversion_rate: number;
}

export interface SourceRow {
  source: string | null;
  source_quality: string | null;
  total: number;
  responded: number;
  response_rate: number;
}

export interface BenchmarkData {
  mandate_response_rate: number;
  mandate_avg_touches_to_response: number | null;
  mandate_avg_days_to_response: number | null;
  this_company_touches: number;
  this_company_days_to_response: number | null;
}

export function useAnalyticsOverview() {
  return useQuery<OverviewStats>({
    queryKey: ["analytics", "overview"],
    queryFn: () => api.get<OverviewStats>("/analytics/overview"),
    staleTime: 60_000,
  });
}

export function useResponseByBucket() {
  return useQuery<{ items: BucketRow[] }>({
    queryKey: ["analytics", "response-by-bucket"],
    queryFn: () => api.get<{ items: BucketRow[] }>("/analytics/response-by-bucket"),
    staleTime: 60_000,
  });
}

export function useByAnalyst() {
  return useQuery<{ items: AnalystRow[] }>({
    queryKey: ["analytics", "by-analyst"],
    queryFn: () => api.get<{ items: AnalystRow[] }>("/analytics/by-analyst"),
    staleTime: 60_000,
  });
}

export function useSources() {
  return useQuery<{ items: SourceRow[] }>({
    queryKey: ["analytics", "sources"],
    queryFn: () => api.get<{ items: SourceRow[] }>("/analytics/sources"),
    staleTime: 60_000,
  });
}

export function useBenchmark(companyId: number) {
  return useQuery<BenchmarkData>({
    queryKey: ["benchmark", companyId],
    queryFn: () => api.get<BenchmarkData>(`/companies/${companyId}/benchmark`),
    staleTime: 60_000,
    enabled: companyId > 0,
  });
}
