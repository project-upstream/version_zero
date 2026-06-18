import {
  BarChart3,
  Briefcase,
  Building2,
  CalendarClock,
  LayoutDashboard,
  Settings,
  Users,
  type LucideIcon,
} from "lucide-react";

import type { Role } from "@/types";

export interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
  /** If set, only these roles see the item. Undefined = visible to all. */
  roles?: Role[];
}

export const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Companies", href: "/companies", icon: Building2 },
  { label: "Schedule", href: "/schedule", icon: CalendarClock },
  { label: "Contacts", href: "/contacts", icon: Users },
  { label: "Mandates", href: "/mandates", icon: Briefcase },
  { label: "Analytics", href: "/analytics", icon: BarChart3 },
  { label: "Settings", href: "/settings", icon: Settings, roles: ["PARTNER"] },
];

export function visibleNav(role: Role): NavItem[] {
  return NAV_ITEMS.filter((item) => !item.roles || item.roles.includes(role));
}
