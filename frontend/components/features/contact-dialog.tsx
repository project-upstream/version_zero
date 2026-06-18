"use client";

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";

import { useCreateContact, useUpdateContact } from "@/hooks/use-contacts";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type { Contact } from "@/types";

const ENGAGEMENT_OPTIONS = [
  { value: "", label: "None" },
  { value: "BUY_SIDE", label: "Buy-side" },
  { value: "SELL_SIDE", label: "Sell-side" },
  { value: "CAPITAL_RAISE", label: "Capital raise" },
];

const schema = z.object({
  contact_person: z.string().min(1, "Name is required"),
  designation: z.string().optional(),
  email: z.string().email("Invalid email").optional().or(z.literal("")),
  phone: z.string().optional(),
  engagement: z.string().optional(),
  remark: z.string().optional(),
  is_primary: z.boolean().optional(),
});

type FormValues = z.infer<typeof schema>;

interface Props {
  companyId: number;
  contact?: Contact;
  trigger?: React.ReactNode;
  onSuccess?: () => void;
}

export function ContactDialog({ companyId, contact, trigger, onSuccess }: Props) {
  const [open, setOpen] = useState(false);
  const createContact = useCreateContact();
  const updateContact = useUpdateContact();

  const isEdit = !!contact;

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      contact_person: contact?.contact_person ?? "",
      designation: contact?.designation ?? "",
      email: contact?.email ?? "",
      phone: contact?.phone ?? "",
      engagement: contact?.engagement ?? "",
      remark: contact?.remark ?? "",
      is_primary: contact?.is_primary ?? false,
    },
  });

  useEffect(() => {
    if (open) {
      reset({
        contact_person: contact?.contact_person ?? "",
        designation: contact?.designation ?? "",
        email: contact?.email ?? "",
        phone: contact?.phone ?? "",
        engagement: contact?.engagement ?? "",
        remark: contact?.remark ?? "",
        is_primary: contact?.is_primary ?? false,
      });
    }
  }, [open, contact, reset]);

  const onSubmit = async (data: FormValues) => {
    const payload: Record<string, unknown> = {
      ...data,
      engagement: data.engagement || null,
      email: data.email || null,
    };
    try {
      if (isEdit) {
        await updateContact.mutateAsync({ id: contact.id, data: payload });
        toast.success("Contact updated");
      } else {
        await createContact.mutateAsync({ ...payload, company_id: companyId });
        toast.success("Contact created");
      }
      reset();
      setOpen(false);
      onSuccess?.();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Failed to save contact";
      toast.error(msg);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <span className="contents" onClick={() => setOpen(true)}>
        {trigger ?? (
          <Button size="sm">{isEdit ? "Edit" : "Add contact"}</Button>
        )}
      </span>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>{isEdit ? "Edit contact" : "Add contact"}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 pt-2">
          <div>
            <Label htmlFor="contact_person">Name *</Label>
            <Input
              id="contact_person"
              {...register("contact_person")}
              className="mt-1"
            />
            {errors.contact_person && (
              <p className="mt-1 text-xs text-destructive">{errors.contact_person.message}</p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label htmlFor="designation">Designation</Label>
              <Input id="designation" {...register("designation")} className="mt-1" />
            </div>
            <div>
              <Label htmlFor="engagement">Engagement</Label>
              <select
                id="engagement"
                {...register("engagement")}
                className="mt-1 w-full h-9 rounded-md border border-input bg-background px-3 text-sm"
              >
                {ENGAGEMENT_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" {...register("email")} className="mt-1" />
              {errors.email && (
                <p className="mt-1 text-xs text-destructive">{errors.email.message}</p>
              )}
            </div>
            <div>
              <Label htmlFor="phone">Phone</Label>
              <Input id="phone" {...register("phone")} className="mt-1" />
            </div>
          </div>

          <div>
            <Label htmlFor="remark">Remark</Label>
            <Input id="remark" {...register("remark")} className="mt-1" />
          </div>

          <div className="flex items-center gap-2">
            <input type="checkbox" id="is_primary" {...register("is_primary")} />
            <Label htmlFor="is_primary">Primary contact for company</Label>
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
