import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "@/components/app/shell";
import { PageHeader, StatusPill } from "@/components/app/primitives";
import { DataTable } from "@/components/app/data-table";
import { networkApi, NetworkDevice } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle, Network as NetIcon, RefreshCw } from "lucide-react";

export const Route = createFileRoute("/infrastructure/network")({
  head: () => ({ meta: [{ title: "Networking — CloudAxis" }] }),
  component: () => (
    <AppShell>
      <Networking />
    </AppShell>
  ),
});

function Networking() {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["network"],
    queryFn: () => networkApi.list(),
  });

  const devices: NetworkDevice[] = data?.items || [];

  return (
    <>
      <PageHeader
        eyebrow="Infrastructure"
        title="Networking"
        subtitle={isLoading ? "Loading network devices…" : `${devices.length} network devices`}
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
          <h3 className="mt-4 text-base font-semibold">Failed to load network devices</h3>
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
          rows={devices}
          columns={[
            {
              key: "name",
              label: "Device",
              render: (n) => (
                <div className="flex items-center gap-2">
                  <span className="grid h-8 w-8 place-items-center rounded-lg bg-info/15 text-info">
                    <NetIcon className="h-4 w-4" />
                  </span>
                  <div>
                    <div className="font-medium">{n.name}</div>
                    <div className="text-xs text-muted-foreground">{n.vendor || "Generic"}</div>
                  </div>
                </div>
              ),
            },
            { key: "type", label: "Type" },
            { key: "ip", label: "IP", render: (n) => n.ip || "—" },
            { key: "throughputGbps", label: "Throughput", render: (n) => `${n.throughputGbps ?? 0} Gbps` },
            { key: "latencyMs", label: "Latency", render: (n) => `${n.latencyMs ?? 0} ms` },
            { key: "packetLoss", label: "Loss", render: (n) => `${n.packetLoss ?? 0}%` },
            { key: "status", label: "Status", render: (n) => <StatusPill status={n.status} /> },
          ]}
        />
      )}
    </>
  );
}
