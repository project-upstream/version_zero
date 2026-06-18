"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";

import { useLogEvent } from "@/hooks/use-schedule";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

const EVENT_TYPES = [
  { value: "INITIAL_EMAIL", label: "Initial email" },
  { value: "FOLLOW_UP", label: "Follow-up" },
  { value: "RESPONSE", label: "Response received" },
  { value: "BOUNCE", label: "Bounce" },
  { value: "CALL", label: "Call" },
  { value: "LINKEDIN", label: "LinkedIn" },
  { value: "MEETING", label: "Meeting" },
  { value: "NOTE", label: "Note" },
];

const schema = z.object({
  event_type: z.string().min(1),
  occurred_on: z.string().min(1),
  notes: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

interface Props {
  companyId: number;
  companyName: string;
  trigger?: React.ReactNode;
  defaultEventType?: string;
}

export function LogOutreachDialog({
  companyId,
  companyName,
  trigger,
  defaultEventType,
}: Props) {
  const [open, setOpen] = useState(false);
  const logEvent = useLogEvent(companyId);

  const today = new Date().toISOString().split("T")[0];
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      event_type: defaultEventType ?? "FOLLOW_UP",
      occurred_on: today,
    },
  });

  const onSubmit = async (data: FormValues) => {
    try {
      await logEvent.mutateAsync(data);
      toast.success("Outreach logged");
      reset();
      setOpen(false);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Failed to log outreach";
      toast.error(msg);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      {/* @base-ui DialogTrigger uses render= not asChild; use a click wrapper instead */}
      <span className="contents" onClick={() => setOpen(true)}>
        {trigger ?? <Button size="sm">Log outreach</Button>}
      </span>
      <DialogContent className="max-w-sm">
        <DialogHeader>
          <DialogTitle>Log outreach — {companyName}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 pt-2">
          <div>
            <Label htmlFor="event_type">Type</Label>
            <select
              id="event_type"
              {...register("event_type")}
              className="mt-1 w-full h-9 rounded-md border border-input bg-background px-3 text-sm"
            >
              {EVENT_TYPES.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <Label htmlFor="occurred_on">Date</Label>
            <Input
              id="occurred_on"
              type="date"
              {...register("occurred_on")}
              className="mt-1"
            />
            {errors.occurred_on && (
              <p className="mt-1 text-xs text-destructive">{errors.occurred_on.message}</p>
            )}
          </div>

          <div>
            <Label htmlFor="notes">Notes (optional)</Label>
            <Input
              id="notes"
              {...register("notes")}
              placeholder="Brief notes..."
              className="mt-1"
            />
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="ghost" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Saving..." : "Save"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
