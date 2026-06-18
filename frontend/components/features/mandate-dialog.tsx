"use client";

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";

import { useCreateMandate, useUpdateMandate } from "@/hooks/use-mandates";
import { useUsers } from "@/hooks/use-users";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type { MandateDetail } from "@/types";

const TYPE_OPTIONS = [
  { value: "SELL_SIDE", label: "Sell-side" },
  { value: "BUY_SIDE", label: "Buy-side" },
  { value: "CAPITAL_RAISE", label: "Capital raise" },
];

const STATUS_OPTIONS = [
  { value: "ACTIVE", label: "Active" },
  { value: "ON_HOLD", label: "On hold" },
  { value: "CLOSED", label: "Closed" },
  { value: "TERMINATED", label: "Terminated" },
];

const schema = z.object({
  client_name: z.string().min(1, "Client name is required"),
  name: z.string().min(1, "Mandate name is required"),
  type: z.string().min(1),
  status: z.string().min(1),
  lead_owner_id: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

interface Props {
  mandate?: MandateDetail;
  trigger?: React.ReactNode;
}

export function MandateDialog({ mandate, trigger }: Props) {
  const [open, setOpen] = useState(false);
  const createMandate = useCreateMandate();
  const updateMandate = useUpdateMandate();
  const { data: users } = useUsers();
  const isEdit = !!mandate;

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      client_name: mandate?.client_name ?? "",
      name: mandate?.name ?? "",
      type: mandate?.type ?? "SELL_SIDE",
      status: mandate?.status ?? "ACTIVE",
      lead_owner_id: mandate?.lead_owner_id ? String(mandate.lead_owner_id) : "",
    },
  });

  useEffect(() => {
    if (open) {
      reset({
        client_name: mandate?.client_name ?? "",
        name: mandate?.name ?? "",
        type: mandate?.type ?? "SELL_SIDE",
        status: mandate?.status ?? "ACTIVE",
        lead_owner_id: mandate?.lead_owner_id ? String(mandate.lead_owner_id) : "",
      });
    }
  }, [open, mandate, reset]);

  const onSubmit = async (data: FormValues) => {
    const payload: Record<string, unknown> = {
      client_name: data.client_name,
      name: data.name,
      type: data.type,
      status: data.status,
      lead_owner_id: data.lead_owner_id ? Number(data.lead_owner_id) : null,
    };
    try {
      if (isEdit) {
        await updateMandate.mutateAsync({ id: mandate.id, data: payload });
        toast.success("Mandate updated");
      } else {
        await createMandate.mutateAsync(payload);
        toast.success("Mandate created");
      }
      reset();
      setOpen(false);
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : "Failed to save mandate");
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <span className="contents" onClick={() => setOpen(true)}>
        {trigger ?? <Button size="sm">New mandate</Button>}
      </span>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>{isEdit ? "Edit mandate" : "New mandate"}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 pt-2">
          <div>
            <Label htmlFor="client_name">Client *</Label>
            <Input id="client_name" {...register("client_name")} className="mt-1" />
            {errors.client_name && (
              <p className="mt-1 text-xs text-destructive">{errors.client_name.message}</p>
            )}
          </div>

          <div>
            <Label htmlFor="name">Mandate name *</Label>
            <Input id="name" {...register("name")} className="mt-1" />
            {errors.name && (
              <p className="mt-1 text-xs text-destructive">{errors.name.message}</p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label htmlFor="type">Type</Label>
              <select
                id="type"
                {...register("type")}
                className="mt-1 w-full h-9 rounded-md border border-input bg-background px-3 text-sm"
              >
                {TYPE_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>
            <div>
              <Label htmlFor="status">Status</Label>
              <select
                id="status"
                {...register("status")}
                className="mt-1 w-full h-9 rounded-md border border-input bg-background px-3 text-sm"
              >
                {STATUS_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <Label htmlFor="lead_owner_id">Lead owner</Label>
            <select
              id="lead_owner_id"
              {...register("lead_owner_id")}
              className="mt-1 w-full h-9 rounded-md border border-input bg-background px-3 text-sm"
            >
              <option value="">Unassigned</option>
              {users?.items.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.full_name} ({u.role.toLowerCase()})
                </option>
              ))}
            </select>
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
