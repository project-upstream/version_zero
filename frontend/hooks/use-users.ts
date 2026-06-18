"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { FirmUser } from "@/types";

export function useUsers() {
  return useQuery<{ items: FirmUser[] }>({
    queryKey: ["users"],
    queryFn: () => api.get<{ items: FirmUser[] }>("/users"),
    staleTime: 5 * 60 * 1000,
  });
}
