"use client";

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

import { useCreateCompany } from "@/hooks/use-companies";
import { useMandates } from "@/hooks/use-mandates";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

const TYPE_OPTIONS = [
  { value: "TARGET", label: "Target" },
  { value: "BUYER", label: "Buyer" },
  { value: "INVESTOR", label: "Investor" },
];

const SOURCE_OPTIONS = [
  { value: "PROPRIETARY", label: "Proprietary" },
  { value: "PUBLIC", label: "Public" },
  { value: "REFERRAL", label: "Referral" },
  { value: "IMPORTED", label: "Imported" },
];

const schema = z.object({
  company_name: z.string().min(1, "Company name is required"),
  mandate_id: z.string().min(1, "Mandate is required"),
  type: z.string().min(1),
  hq: z.string().optional(),
  bucket: z.string().optional(),
  source: z.string().optional(),
  website: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

interface Props {
  defaultMandateId?: number;
  trigger?: React.ReactNode;
}

export function CompanyDialog({ defaultMandateId, trigger }: Props) {
  const [open, setOpen] = useState(false);
  const router = useRouter();
  const createCompany = useCreateCompany();
  const { data: mandates } = useMandates();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      company_name: "",
      mandate_id: defaultMandateId ? String(defaultMandateId) : "",
      type: "TARGET",
      source: "PROPRIETARY",
    },
  });

  useEffect(() => {
    if (open) {
      reset({
        company_name: "",
        mandate_id: defaultMandateId ? String(defaultMandateId) : "",
        type: "TARGET",
        source: "PROPRIETARY",
        hq: "",
        bucket: "",
        website: "",
      });
    }
  }, [open, defaultMandateId, reset]);

  const onSubmit = async (data: FormValues) => {
    const payload: Record<string, unknown> = {
      company_name: data.company_name,
      mandate_id: Number(data.mandate_id),
      type: data.type,
      hq: data.hq || null,
      bucket: data.bucket || null,
      source: data.source || "PROPRIETARY",
      website: data.website || null,
    };
    try {
      const created = await createCompany.mutateAsync(payload);
      const dupes = created.duplicate_warnings ?? [];
      if (dupes.length > 0) {
        toast.warning(
          `Created — but ${dupes.length} possible duplicate${dupes.length > 1 ? "s" : ""} across mandates`
        );
      } else {
        toast.success("Company created");
      }
      reset();
      setOpen(false);
      router.push(`/companies/${created.id}`);
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : "Failed to create company");
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <span className="contents" onClick={() => setOpen(true)}>
        {trigger ?? <Button size="sm">New company</Button>}
      </span>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>New company</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 pt-2">
          <div>
            <Label htmlFor="company_name">Company name *</Label>
            <Input id="company_name" {...register("company_name")} className="mt-1" />
            {errors.company_name && (
              <p className="mt-1 text-xs text-destructive">{errors.company_name.message}</p>
            )}
          </div>

          <div>
            <Label htmlFor="mandate_id">Mandate *</Label>
            <select
              id="mandate_id"
              {...register("mandate_id")}
              className="mt-1 w-full h-9 rounded-md border border-input bg-background px-3 text-sm"
            >
              <option value="">Select a mandate…</option>
              {mandates?.items.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.name} — {m.client_name}
                </option>
              ))}
            </select>
            {errors.mandate_id && (
              <p className="mt-1 text-xs text-destructive">{errors.mandate_id.message}</p>
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
              <Label htmlFor="source">Source</Label>
              <select
                id="source"
                {...register("source")}
                className="mt-1 w-full h-9 rounded-md border border-input bg-background px-3 text-sm"
              >
                {SOURCE_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label htmlFor="hq">HQ</Label>
              <Input id="hq" {...register("hq")} className="mt-1" />
            </div>
            <div>
              <Label htmlFor="bucket">Bucket</Label>
              <Input id="bucket" {...register("bucket")} className="mt-1" />
            </div>
          </div>

          <div>
            <Label htmlFor="website">Website</Label>
            <Input id="website" {...register("website")} placeholder="https://" className="mt-1" />
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="ghost" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Creating..." : "Create"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
