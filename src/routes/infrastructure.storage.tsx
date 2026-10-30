import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "@/components/app/shell";
import { Card, PageHeader, StatusPill } from "@/components/app/primitives";
import { storageApi, Datastore } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle, RefreshCw } from "lucide-react";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { seriesTimeline } from "@/lib/mock-data";

export const Route = createFileRoute("/infrastructure/storage")({
  head: () => ({ meta: [{ title: "Storage — CloudAxis" }] }),
  component: () => (
    <AppShell>
      <Storage />
    </AppShell>
  ),
});

function Storage() {
  const trend = seriesTimeline(24, 60, 20, 33);

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["storage"],
    queryFn: () => storageApi.list(),
  });

  const datastores: Datastore[] = data?.items || [];
  const totalProvisionedTB = datastores.reduce((s, d) => s + (d.capacityTB || 0), 0);

  return (
    <>
      <PageHeader
        eyebrow="Infrastructure"
        title="Storage & Datastores"
        subtitle={
          isLoading
            ? "Loading datastores…"
            : `${datastores.length} datastores · ${totalProvisionedTB.toFixed(1)} TB provisioned`
        }
      />
      <Card className="mb-6">
        <div className="mb-2 text-sm font-semibold">Aggregate capacity trend (24h)</div>
        <div className="h-56">
          <ResponsiveContainer>
            <AreaChart data={trend}>
              <defs>
                <linearGradient id="stor" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="0%" stopColor="var(--color-info)" stopOpacity={0.5} />
                  <stop offset="100%" stopColor="var(--color-info)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="t" stroke="var(--color-muted-foreground)" fontSize={10} />
              <YAxis stroke="var(--color-muted-foreground)" fontSize={10} />
              <Tooltip contentStyle={{ background: "var(--color-popover)", border: "1px solid var(--color-border)", borderRadius: 12 }} />
              <Area type="monotone" dataKey="storage" stroke="var(--color-info)" fill="url(#stor)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="p-6">
              <Skeleton className="mb-2 h-6 w-1/3" />
              <Skeleton className="mb-4 h-4 w-1/2" />
              <Skeleton className="mb-2 h-10 w-1/4" />
              <Skeleton className="h-2 w-full rounded-full" />
            </Card>
          ))}
        </div>
      ) : isError ? (
        <div className="flex flex-col items-center justify-center rounded-2xl border border-destructive/20 bg-destructive/5 p-10 text-center">
          <AlertCircle className="h-10 w-10 text-destructive" />
          <h3 className="mt-4 text-base font-semibold">Failed to load storage</h3>
          <p className="mt-1 text-xs text-muted-foreground">{(error as any)?.message || "Network error occurred"}</p>
          <button
            onClick={() => refetch()}
            className="mt-4 inline-flex items-center gap-2 rounded-lg bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground"
          >
            <RefreshCw className="h-3.5 w-3.5" /> Try again
          </button>
        </div>
      ) : datastores.length === 0 ? (
        <Card className="p-8 text-center text-muted-foreground">No datastores found.</Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {datastores.map((d) => {
            const capacity = d.capacityTB || 1;
            const used = d.usedTB || 0;
            const pct = Math.min(100, Math.max(0, Math.round((used / capacity) * 100)));
            return (
              <Card key={d.id}>
                <div className="flex items-start justify-between">
                  <div>
                    <div className="text-xs uppercase tracking-widest text-muted-foreground">{d.type}</div>
                    <div className="text-lg font-semibold">{d.name}</div>
                    <div className="text-xs text-muted-foreground">{d.location || "Local"}</div>
                  </div>
                  <StatusPill status={d.status} />
                </div>
                <div className="mt-4 flex items-end justify-between">
                  <div>
                    <div className="text-3xl font-bold tabular-nums">{pct}%</div>
                    <div className="text-xs text-muted-foreground">
                      {used} TB / {capacity} TB
                    </div>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {Math.max(0, capacity - used).toFixed(1)} TB free
                  </div>
                </div>
                <div className="mt-4 h-2 rounded-full bg-secondary">
                  <div
                    className={`h-2 rounded-full ${pct > 85 ? "bg-destructive" : pct > 70 ? "bg-accent" : "bg-success"}`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </>
  );
}
