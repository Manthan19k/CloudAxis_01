import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { AppShell } from "@/components/app/shell";
import { PageHeader, StatusPill } from "@/components/app/primitives";
import { DataTable } from "@/components/app/data-table";
import { alertsApi, Alert } from "@/lib/api";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle, AlertTriangle, Check, RefreshCw } from "lucide-react";
import { toast } from "sonner";

export const Route = createFileRoute("/alerts")({
  head: () => ({ meta: [{ title: "Alerts — CloudAxis" }] }),
  component: () => (
    <AppShell>
      <Alerts />
    </AppShell>
  ),
});

function Alerts() {
  const queryClient = useQueryClient();
  const [filter, setFilter] = useState<"all" | "critical" | "warning" | "info">("all");

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["alerts"],
    queryFn: () => alertsApi.list(),
  });

  const ackMutation = useMutation({
    mutationFn: (id: string | number) => alertsApi.update(id, { acknowledged: true }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      toast.success("Acknowledged");
    },
    onError: (err: any) => {
      toast.error(err.message || "Failed to acknowledge alert");
    },
  });

  const resolveMutation = useMutation({
    mutationFn: (id: string | number) => alertsApi.update(id, { resolved: true, acknowledged: true }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      toast.success("Resolved");
    },
    onError: (err: any) => {
      toast.error(err.message || "Failed to resolve alert");
    },
  });

  const rows: Alert[] = data?.items || [];
  const filtered = filter === "all" ? rows : rows.filter((r) => r.severity === filter);
  const unacknowledgedCount = rows.filter((r) => !r.acknowledged).length;

  return (
    <>
      <PageHeader
        eyebrow="Operations"
        title="Alert Center"
        subtitle={isLoading ? "Loading alerts…" : `${unacknowledgedCount} unacknowledged`}
        actions={
          <div className="inline-flex rounded-lg border border-border bg-card p-1">
            {(["all", "critical", "warning", "info"] as const).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`rounded-md px-3 py-1.5 text-xs capitalize ${filter === f ? "bg-primary text-primary-foreground" : "text-muted-foreground"}`}
              >
                {f}
              </button>
            ))}
          </div>
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
          <h3 className="mt-4 text-base font-semibold">Failed to load alerts</h3>
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
          rows={filtered}
          columns={[
            {
              key: "title",
              label: "Alert",
              render: (a) => (
                <div className="flex items-center gap-2">
                  <span
                    className={`grid h-8 w-8 place-items-center rounded-lg ${
                      a.severity === "critical"
                        ? "bg-destructive/15 text-destructive"
                        : a.severity === "warning"
                          ? "bg-accent/15 text-accent"
                          : "bg-info/15 text-info"
                    }`}
                  >
                    <AlertTriangle className="h-4 w-4" />
                  </span>
                  <div>
                    <div className="font-medium">{a.title}</div>
                    <div className="text-xs text-muted-foreground">{a.source}</div>
                  </div>
                </div>
              ),
            },
            { key: "severity", label: "Severity", render: (a) => <StatusPill status={a.severity} /> },
            { key: "assignee", label: "Assignee", render: (a) => a.assignee ?? <span className="text-muted-foreground">Unassigned</span> },
            {
              key: "triggeredAt",
              label: "Triggered",
              render: (a) => {
                const dateVal = a.triggeredAt ? new Date(a.triggeredAt) : null;
                return dateVal && !isNaN(dateVal.getTime())
                  ? dateVal.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })
                  : a.time || "Just now";
              },
            },
            {
              key: "acknowledged",
              label: "State",
              render: (a) => (
                <StatusPill status={a.resolved ? "healthy" : a.acknowledged ? "warning" : "critical"} />
              ),
            },
            {
              key: "id",
              label: "Actions",
              sortable: false,
              render: (a) => (
                <div className="flex gap-1">
                  {!a.acknowledged ? (
                    <button
                      disabled={ackMutation.isPending}
                      onClick={(e) => {
                        e.stopPropagation();
                        ackMutation.mutate(a.alertId || a.id);
                      }}
                      className="rounded-md border border-border px-2 py-1 text-xs hover:text-foreground disabled:opacity-50"
                    >
                      Ack
                    </button>
                  ) : null}
                  {!a.resolved ? (
                    <button
                      disabled={resolveMutation.isPending}
                      onClick={(e) => {
                        e.stopPropagation();
                        resolveMutation.mutate(a.alertId || a.id);
                      }}
                      className="inline-flex items-center gap-1 rounded-md border border-success/30 bg-success/10 px-2 py-1 text-xs text-success disabled:opacity-50"
                    >
                      <Check className="h-3 w-3" /> Resolve
                    </button>
                  ) : null}
                </div>
              ),
            },
          ]}
        />
      )}
    </>
  );
}
