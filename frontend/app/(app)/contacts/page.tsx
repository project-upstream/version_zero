"use client";

import { useState } from "react";
import Link from "next/link";
import { User, Search } from "lucide-react";

import { useContacts } from "@/hooks/use-contacts";
import { PageHeader } from "@/components/layout/page-header";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { TableSkeleton } from "@/components/features/table-skeleton";
import { EmptyState } from "@/components/features/empty-state";
import type { Contact } from "@/types";

const ENGAGEMENT_OPTIONS = [
  { value: "", label: "All engagements" },
  { value: "BUY_SIDE", label: "Buy-side" },
  { value: "SELL_SIDE", label: "Sell-side" },
  { value: "CAPITAL_RAISE", label: "Capital raise" },
];

function ContactRow({ contact }: { contact: Contact }) {
  return (
    <Link
      href={`/contacts/${contact.id}`}
      className="flex items-start justify-between py-4 gap-4 hover:bg-muted/40 px-4 rounded-lg transition-colors"
    >
      <div className="flex items-start gap-3">
        <div className="mt-0.5 h-8 w-8 rounded-full bg-muted flex items-center justify-center flex-shrink-0">
          <User className="h-4 w-4 text-muted-foreground" />
        </div>
        <div>
          <p className="font-medium text-sm">
            {contact.contact_person}
            {contact.is_primary && (
              <Badge variant="secondary" className="ml-2 text-[10px]">Primary</Badge>
            )}
          </p>
          {contact.designation && (
            <p className="text-xs text-muted-foreground">{contact.designation}</p>
          )}
          {contact.email && (
            <p className="text-xs text-muted-foreground">{contact.email}</p>
          )}
        </div>
      </div>
      <div className="text-right text-xs text-muted-foreground shrink-0 space-y-0.5">
        {contact.engagement && <p>{contact.engagement.replace("_", "-")}</p>}
        {contact.last_contact_date && (
          <p>Last: {contact.last_contact_date}</p>
        )}
        {contact.archived_at && (
          <Badge variant="outline" className="text-[10px]">Archived</Badge>
        )}
      </div>
    </Link>
  );
}

export default function ContactsPage() {
  const [q, setQ] = useState("");
  const [engagement, setEngagement] = useState("");
  const [includeArchived, setIncludeArchived] = useState(false);
  const [debouncedQ, setDebouncedQ] = useState("");

  const { data, isLoading } = useContacts({
    q: debouncedQ || undefined,
    engagement: engagement || undefined,
    include_archived: includeArchived || undefined,
  });

  const handleSearch = (value: string) => {
    setQ(value);
    clearTimeout((window as unknown as Record<string, ReturnType<typeof setTimeout>>)._contactSearchTimer);
    (window as unknown as Record<string, ReturnType<typeof setTimeout>>)._contactSearchTimer = setTimeout(
      () => setDebouncedQ(value),
      300
    );
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      <PageHeader
        title="Contacts"
        description={data ? `${data.total} contact${data.total !== 1 ? "s" : ""}` : undefined}
      />

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-48">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search contacts..."
            value={q}
            onChange={(e) => handleSearch(e.target.value)}
            className="pl-9"
          />
        </div>

        <select
          value={engagement}
          onChange={(e) => setEngagement(e.target.value)}
          className="h-9 rounded-md border border-input bg-background px-3 text-sm"
        >
          {ENGAGEMENT_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>

        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={includeArchived}
            onChange={(e) => setIncludeArchived(e.target.checked)}
          />
          Show archived
        </label>
      </div>

      {/* List */}
      {isLoading ? (
        <TableSkeleton rows={8} />
      ) : !data || data.total === 0 ? (
        <EmptyState
          icon={User}
          title="No contacts"
          description="Contacts are added from the company detail page."
        />
      ) : (
        <div className="divide-y rounded-lg border">
          {data.items.map((c) => (
            <ContactRow key={c.id} contact={c} />
          ))}
        </div>
      )}
    </div>
  );
}
