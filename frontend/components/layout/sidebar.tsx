"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { visibleNav } from "@/components/layout/nav";
import { useAuth } from "@/hooks/use-auth";
import { cn } from "@/lib/utils";

export function Sidebar() {
  const pathname = usePathname();
  const { user } = useAuth();
  const items = visibleNav(user?.role ?? "ANALYST");

  return (
    <aside className="bg-sidebar text-sidebar-foreground hidden w-60 shrink-0 flex-col border-r md:flex" style={{ borderColor: "var(--sidebar-border)" }}>
      {/* Brand */}
      <div className="flex h-14 items-center gap-2 border-b px-4" style={{ borderColor: "var(--sidebar-border)" }}>
        <span
          className="text-foreground text-lg font-semibold tracking-tight"
          style={{ fontFamily: "var(--font-display)", fontSize: "20px" }}
        >
          Upstream
        </span>
      </div>

      <nav className="flex-1 space-y-0.5 overflow-y-auto p-2">
        {items.map((item) => {
          const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "nav-item flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium",
                active
                  ? "active bg-primary/10 text-foreground"
                  : "text-muted-foreground hover:bg-foreground/[0.04] hover:text-foreground",
              )}
            >
              <Icon
                className={cn("size-4 shrink-0", active ? "text-primary" : "")}
              />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t p-4 text-xs" style={{ borderColor: "var(--sidebar-border)" }}>
        <p className="text-muted-foreground truncate">{user?.firm?.name ?? "Upstream"}</p>
      </div>
    </aside>
  );
}
