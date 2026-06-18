"use client";

import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";
import type { CurrentUser } from "@/types";

/**
 * Returns the authenticated user from GET /auth/me (cookie-based).
 *
 * - isLoading true while the request is in-flight (show skeleton/spinner).
 * - user null + isLoading false means 401 → apiFetch already redirected to /login.
 */
export function useAuth(): { user: CurrentUser | null; isLoading: boolean } {
  const { data, isLoading } = useQuery<CurrentUser>({
    queryKey: ["auth", "me"],
    queryFn: () => api.get<CurrentUser>("/auth/me"),
    retry: false,
    staleTime: 5 * 60 * 1000, // 5 min — re-validate after tab focus, etc.
  });

  return { user: data ?? null, isLoading };
}
