import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "@/components/app/shell";
import { PageHeader, StatusPill } from "@/components/app/primitives";
import { DataTable } from "@/components/app/data-table";
import { vmsApi, VM } from "@/lib/api";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle, Boxes, Plus, RefreshCw } from "lucide-react";
import { toast } from "sonner";

export const Route = createFileRoute("/infrastructure/vms")({
  head: () => ({ meta: [{ title: "Virtual Machines — CloudAxis" }] }),
  component: () => (
    <AppShell>
      <VMs />
    </AppShell>
  ),
});

function VMs() {
  const queryClient = useQueryClient();

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["vms"],
    queryFn: () => vmsApi.list(),
  });

  const createMutation = useMutation({
    mutationFn: (newVm: Partial<VM>) => vmsApi.create(newVm),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["vms"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      toast.success("VM provisioned");
    },
    onError: (err: any) => {
      toast.error(err.message || "Failed to provision VM");
    },
  });

  const rows = data?.items || [];
  const hostCount = new Set(rows.map((v) => v.host).filter(Boolean)).size;

  return (
    <>
      <PageHeader
        eyebrow="Infrastructure"
        title="Virtual Machines"
        subtitle={isLoading ? "Loading virtual machines…" : `${rows.length} VMs across ${hostCount} hosts`}
        actions={
          <button
            disabled={createMutation.isPending}
            onClick={() => {
              createMutation.mutate({
                vmId: `VM-${2000 + Math.floor(Math.random() * 8000)}`,
                name: `vm-srv-${rows.length + 1}`,
                host: rows.length > 0 && rows[0].host ? rows[0].host : "Web Server 01",
                os: "Ubuntu 22.04",
                vCPU: 4,
                memoryGB: 16,
                diskGB: 80,
                cpu: 8,
                memory: 20,
                status: "healthy",
                ip: `10.20.0.${rows.length + 10}`,
                owner: "Alex Chen",
                department: "IT",
                snapshots: 0,
              });
            }}
            className="inline-flex items-center gap-1.5 rounded-md bg-primary px-3 py-2 text-xs font-medium text-primary-foreground disabled:opacity-50"
          >
            <Plus className="h-3.5 w-3.5" /> {createMutation.isPending ? "Provisioning…" : "New VM"}
          </button>
        }
      />

      {isLoading ? (
        <div className="space-y-3 rounded-2xl border border-border bg-card p-6 shadow-card">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-16 w-full" />
        </div>
      ) : isError ? (
        <div className="flex flex-col items-center justify-center rounded-2xl border border-destructive/20 bg-destructive/5 p-10 text-center">
          <AlertCircle className="h-10 w-10 text-destructive" />
          <h3 className="mt-4 text-base font-semibold">Failed to load virtual machines</h3>
          <p className="mt-1 text-xs text-muted-foreground">{(error as any)?.message || "Network error occurred"}</p>
          <button
            onClick={() => refetch()}
            className="mt-4 inline-flex items-center gap-2 rounded-lg bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground"
          >
            <RefreshCw className="h-3.5 w-3.5" /> Try again
          </button>
        </div>
      ) : (
        <DataTable
          rows={rows}
          columns={[
            {
              key: "name",
              label: "VM",
              render: (v) => (
                <div className="flex items-center gap-2">
                  <span className="grid h-8 w-8 place-items-center rounded-lg bg-primary/15 text-primary">
                    <Boxes className="h-4 w-4" />
                  </span>
                  <div>
                    <div className="font-medium">{v.name}</div>
                    <div className="text-xs text-muted-foreground">
                      {v.ip} · {v.os}
                    </div>
                  </div>
                </div>
              ),
            },
            { key: "host", label: "Host" },
            { key: "vCPU", label: "vCPU" },
            { key: "memoryGB", label: "Memory", render: (v) => `${v.memoryGB} GB` },
            { key: "diskGB", label: "Disk", render: (v) => `${v.diskGB} GB` },
            { key: "cpu", label: "CPU %", render: (v) => <span className="tabular-nums">{v.cpu}%</span> },
            { key: "snapshots", label: "Snapshots" },
            { key: "status", label: "Status", render: (v) => <StatusPill status={v.status} /> },
          ]}
        />
      )}
    </>
  );
}
