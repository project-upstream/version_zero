"use client";

import { use } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Archive, ArchiveRestore, ExternalLink } from "lucide-react";
import { toast } from "sonner";

import { useContact, useArchiveContact, useUnarchiveContact } from "@/hooks/use-contacts";
import { ContactDialog } from "@/components/features/contact-dialog";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { OutreachEvent } from "@/types";

const EVENT_TYPE_LABELS: Record<string, string> = {
  INITIAL_EMAIL: "Initial email",
  FOLLOW_UP: "Follow-up",
  RESPONSE: "Response",
  BOUNCE: "Bounce",
  CALL: "Call",
  LINKEDIN: "LinkedIn",
  MEETING: "Meeting",
  NOTE: "Note",
};

function Field({ label, value }: { label: string; value: React.ReactNode }) {
  if (value === null || value === undefined || value === "") return null;
  return (
    <div>
      <dt className="text-xs text-muted-foreground uppercase tracking-wide">{label}</dt>
      <dd className="mt-0.5 text-sm">{value}</dd>
    </div>
  );
}

function TouchHistory({ events }: { events: OutreachEvent[] }) {
  if (!events.length) {
    return (
      <p className="py-4 text-center text-sm text-muted-foreground">No outreach recorded yet.</p>
    );
  }

  return (
    <ol className="relative ml-3 border-l border-border">
      {events.map((e) => (
        <li key={e.id} className="mb-6 ml-4">
          <div className="absolute -left-1.5 mt-1.5 h-3 w-3 rounded-full bg-border" />
          <time className="text-xs text-muted-foreground">{e.occurred_on}</time>
          <p className="text-sm font-medium">
            {EVENT_TYPE_LABELS[e.event_type] ?? e.event_type}
          </p>
          {e.notes && <p className="text-xs text-muted-foreground mt-0.5">{e.notes}</p>}
        </li>
      ))}
    </ol>
  );
}

export default function ContactDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();
  const { data: contact, isLoading, error } = useContact(Number(id));
  const archiveContact = useArchiveContact();
  const unarchiveContact = useUnarchiveContact();

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="h-8 w-48 animate-pulse rounded-md bg-muted mb-4" />
        <div className="h-4 w-64 animate-pulse rounded-md bg-muted" />
      </div>
    );
  }

  if (error || !contact) {
    return (
      <div className="p-6">
        <p className="text-sm text-muted-foreground">Contact not found.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Back + actions */}
      <div className="flex items-center justify-between">
        <Button variant="ghost" size="sm" onClick={() => router.back()}>
          <ArrowLeft className="mr-1 h-4 w-4" />
          Back
        </Button>
        <div className="flex gap-2">
          {!contact.archived_at && (
            <>
              <ContactDialog
                companyId={contact.company_id}
                contact={contact}
                trigger={<Button variant="outline" size="sm">Edit</Button>}
              />
              <Button
                variant="outline"
                size="sm"
                onClick={async () => {
                  if (!confirm("Archive this contact?")) return;
                  try {
                    await archiveContact.mutateAsync(contact.id);
                    toast.success("Contact archived");
                    router.back();
                  } catch {
                    toast.error("Failed to archive contact");
                  }
                }}
              >
                <Archive className="mr-1 h-4 w-4" />
                Archive
              </Button>
            </>
          )}
          {contact.archived_at && (
            <>
              <Badge variant="secondary">Archived</Badge>
              <Button
                variant="outline"
                size="sm"
                onClick={async () => {
                  try {
                    await unarchiveContact.mutateAsync(contact.id);
                    toast.success("Contact restored");
                  } catch {
                    toast.error("Failed to restore contact");
                  }
                }}
              >
                <ArchiveRestore className="mr-1 h-4 w-4" />
                Restore
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Header */}
      <PageHeader
        title={contact.contact_person}
        description={[contact.designation, contact.email].filter(Boolean).join(" · ") || undefined}
      />

      <div className="grid gap-6 sm:grid-cols-2">
        {/* Contact details */}
        <Card>
          <CardHeader><CardTitle className="text-sm">Details</CardTitle></CardHeader>
          <CardContent>
            <dl className="grid grid-cols-2 gap-x-4 gap-y-3">
              <Field label="Designation" value={contact.designation} />
              <Field label="Engagement" value={contact.engagement?.replace("_", "-")} />
              <Field label="Email" value={contact.email} />
              <Field label="Phone" value={contact.phone} />
              <Field label="Date connected" value={contact.date_connected} />
              <Field label="Last contact" value={contact.last_contact_date} />
              {contact.linkedin && (
                <div>
                  <dt className="text-xs text-muted-foreground uppercase tracking-wide">LinkedIn</dt>
                  <dd className="mt-0.5 text-sm">
                    <a
                      href={contact.linkedin}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-primary hover:underline"
                    >
                      <ExternalLink className="h-3 w-3" /> Profile
                    </a>
                  </dd>
                </div>
              )}
              <Field label="Primary" value={contact.is_primary ? "Yes" : null} />
            </dl>
            {contact.remark && (
              <div className="mt-4 pt-4 border-t">
                <dt className="text-xs text-muted-foreground uppercase tracking-wide">Remark</dt>
                <dd className="mt-1 text-sm">{contact.remark}</dd>
              </div>
            )}
            {contact.comments && (
              <div className="mt-3">
                <dt className="text-xs text-muted-foreground uppercase tracking-wide">Comments</dt>
                <dd className="mt-1 text-sm">{contact.comments}</dd>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Touch history */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">
              Touch history ({contact.events.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <TouchHistory events={contact.events} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
