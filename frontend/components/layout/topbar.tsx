"use client";

import { ChevronDown, LogOut, UserRound } from "lucide-react";
import { useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuth } from "@/hooks/use-auth";
import { api } from "@/lib/api";
import { ThemeToggle } from "@/components/layout/theme-toggle";

const ROLE_LABEL: Record<string, string> = {
  ANALYST: "Analyst",
  PARTNER: "Partner",
};

export function Topbar() {
  const { user } = useAuth();
  const router = useRouter();
  const queryClient = useQueryClient();

  async function handleLogout() {
    try {
      await api.post("/auth/logout");
    } catch {
      // even if the call fails, drop local state and bounce to login
    }
    queryClient.clear();
    router.push("/login");
  }

  if (!user) return null;

  return (
    <header
      className="flex h-14 shrink-0 items-center justify-between border-b px-4 md:px-6"
      style={{
        background: "var(--background)",
        borderColor: "var(--border)",
        boxShadow: "0 1px 0 oklch(0.72 0.16 58 / 0.06)",
      }}
    >
      <div className="min-w-0">
        <span className="text-sm font-medium">{user.firm.name}</span>
      </div>

      <div className="flex items-center gap-1">
        <ThemeToggle />

        <DropdownMenu>
        <DropdownMenuTrigger render={<Button variant="ghost" size="sm" className="gap-2" />}>
          <span className="bg-primary/10 flex size-7 items-center justify-center rounded-full">
            <UserRound className="text-primary size-4" />
          </span>
          <span className="hidden text-sm sm:inline">{user.full_name}</span>
          <span className="bg-primary/10 text-primary rounded px-1.5 py-0.5 text-xs font-medium">
            {ROLE_LABEL[user.role] ?? user.role}
          </span>
          <ChevronDown className="text-muted-foreground size-4" />
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-48">
          <DropdownMenuGroup>
            <DropdownMenuLabel className="truncate font-normal">{user.email}</DropdownMenuLabel>
          </DropdownMenuGroup>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={handleLogout} variant="destructive">
            <LogOut className="size-4" />
            Log out
          </DropdownMenuItem>
        </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
