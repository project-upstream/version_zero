"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { CompanyListResponse, CompanyDetail, Company, DuplicateWarning } from "@/types";

export interface CreateCompanyResponse extends Company {
  duplicate_warnings?: DuplicateWarning[];
}

export interface CompanyFilters {
  q?: string;
  status?: string;
  type?: string;
  bucket?: string;
  mandate_id?: number;
  source?: string;
  sort?: string;
  page?: number;
  page_size?: number;
  include_archived?: boolean;
}

function buildQS(filters: CompanyFilters): string {
  const p = new URLSearchParams();
  if (filters.q) p.set("q", filters.q);
  if (filters.status) p.set("status", filters.status);
  if (filters.type) p.set("type", filters.type);
  if (filters.bucket) p.set("bucket", filters.bucket);
  if (filters.mandate_id) p.set("mandate_id", String(filters.mandate_id));
  if (filters.source) p.set("source", filters.source);
  if (filters.sort) p.set("sort", filters.sort);
  if (filters.page) p.set("page", String(filters.page));
  if (filters.page_size) p.set("page_size", String(filters.page_size));
  if (filters.include_archived) p.set("include_archived", "true");
  return p.toString() ? `?${p.toString()}` : "";
}

export function useCompanies(filters: CompanyFilters = {}) {
  return useQuery<CompanyListResponse>({
    queryKey: ["companies", filters],
    queryFn: () => api.get<CompanyListResponse>(`/companies${buildQS(filters)}`),
    staleTime: 30_000,
  });
}

export function useCompany(id: number) {
  return useQuery<CompanyDetail>({
    queryKey: ["company", id],
    queryFn: () => api.get<CompanyDetail>(`/companies/${id}`),
    staleTime: 30_000,
  });
}

export function useArchiveCompany() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.del<{ detail: string }>(`/companies/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["companies"] });
    },
  });
}

export function useUnarchiveCompany() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.post<CompanyDetail>(`/companies/${id}/unarchive`),
    onSuccess: (company) => {
      qc.invalidateQueries({ queryKey: ["companies"] });
      qc.setQueryData(["company", company.id], company);
    },
  });
}

export function useCreateCompany() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Record<string, unknown>) =>
      api.post<CreateCompanyResponse>("/companies", data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["companies"] });
      qc.invalidateQueries({ queryKey: ["schedule"] });
      qc.invalidateQueries({ queryKey: ["mandates"] });
    },
  });
}

export function useUpdateCompany() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Record<string, unknown> }) =>
      api.patch<CompanyDetail>(`/companies/${id}`, data),
    onSuccess: (company) => {
      qc.invalidateQueries({ queryKey: ["companies"] });
      qc.setQueryData(["company", company.id], company);
    },
  });
}
