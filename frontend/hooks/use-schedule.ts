"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

export interface ScheduleRow {
  company_id: number;
  company_name: string;
  mandate_id: number;
  company_status: string;
  schedule_id: number;
  schedule_status: string;
  initial_date: string | null;
  next_due_date: string | null;
  days_remaining: number | null;
  is_overdue: boolean;
  cadence_interval_days: number;
  regarding: string | null;
  last_event_date: string | null;
}

export interface ScheduleListResponse {
  items: ScheduleRow[];
  total: number;
}

export interface ScheduleStats {
  sent_this_week: number;
  responses_this_week: number;
  response_rate: number;
  overdue_count: number;
}

export function useNeedsInitial() {
  return useQuery<ScheduleListResponse>({
    queryKey: ["schedule", "needs-initial"],
    queryFn: () => api.get<ScheduleListResponse>("/schedule/needs-initial"),
    staleTime: 30_000,
  });
}

export function useDue(window = 7) {
  return useQuery<ScheduleListResponse>({
    queryKey: ["schedule", "due", window],
    queryFn: () => api.get<ScheduleListResponse>(`/schedule/due?window=${window}`),
    staleTime: 30_000,
  });
}

export function useOverdue() {
  return useQuery<ScheduleListResponse>({
    queryKey: ["schedule", "overdue"],
    queryFn: () => api.get<ScheduleListResponse>("/schedule/overdue"),
    staleTime: 30_000,
  });
}

export function useScheduleStats() {
  return useQuery<ScheduleStats>({
    queryKey: ["schedule", "stats"],
    queryFn: () => api.get<ScheduleStats>("/schedule/stats"),
    staleTime: 30_000,
  });
}

export interface LogEventPayload {
  event_type: string;
  occurred_on: string;
  contact_id?: number;
  regarding?: string;
  notes?: string;
}

export function useLogEvent(companyId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: LogEventPayload) =>
      api.post(`/companies/${companyId}/events`, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["schedule"] });
      qc.invalidateQueries({ queryKey: ["company", companyId] });
      qc.invalidateQueries({ queryKey: ["companies"] });
    },
  });
}

export function usePatchSchedule(companyId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      action,
      data,
    }: {
      action?: "pause" | "resume";
      data?: Record<string, unknown>;
    }) => {
      const qs = action ? `?action=${action}` : "";
      return api.patch(`/companies/${companyId}/schedule${qs}`, data ?? {});
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["company", companyId] });
      qc.invalidateQueries({ queryKey: ["schedule"] });
    },
  });
}
