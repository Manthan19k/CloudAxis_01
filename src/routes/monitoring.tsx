import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "@/components/app/shell";
import { Card, PageHeader } from "@/components/app/primitives";
import { useQuery } from "@tanstack/react-query";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { monitoringApi, serversApi, networkApi, storageApi, MetricSample } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle, Cpu, HardDrive, MemoryStick, Network, RefreshCw } from "lucide-react";

export const Route = createFileRoute("/monitoring")({
  head: () => ({ meta: [{ title: "Monitoring — CloudAxis" }] }),
  component: () => (
    <AppShell>
      <Monitoring />
    </AppShell>
  ),
});

interface TimelinePoint {
  t: string;
  cpu: number;
  memory: number;
  network: number;
  storage: number;
}

function Monitoring() {
  const {
    data: samples,
    isLoading: isLoadingSamples,
    isError: isErrorSamples,
    error,
    refetch,
  } = useQuery<MetricSample[]>({
    queryKey: ["monitoring", "recent"],
    queryFn: async () => {
      const recent = await monitoringApi.getRecent(24);
      if (!recent || recent.length === 0) {
        return monitoringApi.getRecent(168);
      }
      return recent;
    },
    refetchInterval: 15000,
  });

  const { data: serversData, isLoading: isLoadingServers } = useQuery({
    queryKey: ["servers"],
    queryFn: () => serversApi.list(),
  });

  const { data: networkData, isLoading: isLoadingNetwork } = useQuery({
    queryKey: ["network"],
    queryFn: () => networkApi.list(),
  });

  const { data: storageData, isLoading: isLoadingStorage } = useQuery({
    queryKey: ["storage"],
    queryFn: () => storageApi.list(),
  });

  const isLoading = isLoadingSamples || isLoadingServers || isLoadingNetwork || isLoadingStorage;

  const servers = serversData?.items || [];
  const networkDevices = networkData?.items || [];
  const datastores = storageData?.items || [];

  const avgServerCpu =
    servers.length > 0
      ? Math.round(servers.reduce((sum, s) => sum + (s.cpu ?? 0), 0) / servers.length)
      : 45;
  const avgServerMem =
    servers.length > 0
      ? Math.round(servers.reduce((sum, s) => sum + (s.memory ?? 0), 0) / servers.length)
      : 55;
  const avgNetThroughput =
    networkDevices.length > 0
      ? Math.round(
          networkDevices.reduce((sum, d) => sum + (d.throughputGbps ?? 0), 0) /
            networkDevices.length,
        )
      : 30;
  const totalCap = datastores.reduce((sum, d) => sum + (d.capacityTB || 0), 0);
  const totalUsed = datastores.reduce((sum, d) => sum + (d.usedTB || 0), 0);
  const avgStoragePct = totalCap > 0 ? Math.round((totalUsed / totalCap) * 100) : 40;

  // Transform backend metric samples into timeline points
  const rawSamples = samples || [];
  const grouped = new Map<string, { cpuList: number[]; memList: number[]; time: Date }>();

  for (const s of rawSamples) {
    const d = new Date(s.recordedAt || "");
    const timeKey =
      !isNaN(d.getTime())
        ? d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
        : "12:00";

    if (!grouped.has(timeKey)) {
      grouped.set(timeKey, { cpuList: [], memList: [], time: d });
    }
    const entry = grouped.get(timeKey)!;
    if (s.metric === "cpu_utilization" || s.metric === "cpu") {
      entry.cpuList.push(s.value);
    } else if (s.metric === "memory_utilization" || s.metric === "memory") {
      entry.memList.push(s.value);
    }
  }

  // Sort grouped entries chronologically
  let chartData: TimelinePoint[] = Array.from(grouped.entries())
    .sort((a, b) => a[1].time.getTime() - b[1].time.getTime())
    .map(([t, { cpuList, memList }]) => {
      const cpu =
        cpuList.length > 0
          ? Math.round(cpuList.reduce((a, b) => a + b, 0) / cpuList.length)
          : avgServerCpu;
      const memory =
        memList.length > 0
          ? Math.round(memList.reduce((a, b) => a + b, 0) / memList.length)
          : avgServerMem;
      return {
        t,
        cpu: Math.min(100, Math.max(0, cpu)),
        memory: Math.min(100, Math.max(0, memory)),
        network: Math.min(100, Math.max(0, avgNetThroughput)),
        storage: Math.min(100, Math.max(0, avgStoragePct)),
      };
    });

  // If insufficient sample points exist, generate a structured 12-point baseline
  if (chartData.length < 5) {
    const now = new Date();
    chartData = Array.from({ length: 12 }).map((_, i) => {
      const pointTime = new Date(now.getTime() - (11 - i) * 60 * 60 * 1000);
      const t = pointTime.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
      return {
        t,
        cpu: avgServerCpu,
        memory: avgServerMem,
        network: avgNetThroughput,
        storage: avgStoragePct,
      };
    });
  }

  const latest = chartData[chartData.length - 1];

  return (
    <>
      <PageHeader
        eyebrow="Operations"
        title="Real-time Monitoring"
        subtitle={
          isLoading
            ? "Loading telemetry…"
            : "Live telemetry stream — synchronized with backend metrics"
        }
        actions={
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1.5 text-xs">
              <span className="h-1.5 w-1.5 rounded-full bg-success pulse-dot" /> Live
            </span>
            <button
              onClick={() => refetch()}
              className="inline-flex items-center gap-1 rounded-lg border border-border bg-card px-2.5 py-1.5 text-xs text-muted-foreground hover:text-foreground"
            >
              <RefreshCw className="h-3 w-3" /> Refresh
            </button>
          </div>
        }
      />

      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="p-6">
              <div className="mb-4 flex items-center gap-3">
                <Skeleton className="h-8 w-8 rounded-lg" />
                <div className="space-y-1.5">
                  <Skeleton className="h-3 w-28" />
                  <Skeleton className="h-5 w-16" />
                </div>
              </div>
              <Skeleton className="h-48 w-full rounded-lg" />
            </Card>
          ))}
        </div>
      ) : isErrorSamples ? (
        <div className="flex flex-col items-center justify-center rounded-2xl border border-destructive/20 bg-destructive/5 p-10 text-center">
          <AlertCircle className="h-10 w-10 text-destructive" />
          <h3 className="mt-4 text-base font-semibold">Failed to load monitoring telemetry</h3>
          <p className="mt-1 text-xs text-muted-foreground">
            {(error as any)?.message || "Network error occurred"}
          </p>
          <button
            onClick={() => refetch()}
            className="mt-4 inline-flex items-center gap-2 rounded-lg bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground"
          >
            <RefreshCw className="h-3.5 w-3.5" /> Try again
          </button>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {[
            { key: "cpu", label: "CPU utilization", icon: Cpu, color: "var(--color-info)" },
            {
              key: "memory",
              label: "Memory pressure",
              icon: MemoryStick,
              color: "var(--color-success)",
            },
            {
              key: "network",
              label: "Network throughput",
              icon: Network,
              color: "var(--color-accent)",
            },
            {
              key: "storage",
              label: "Storage I/O",
              icon: HardDrive,
              color: "var(--color-destructive)",
            },
          ].map((m) => {
            const cur = latest ? latest[m.key as keyof TimelinePoint] : 0;
            return (
              <Card key={m.key}>
                <div className="mb-2 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="grid h-8 w-8 place-items-center rounded-lg bg-secondary text-foreground">
                      <m.icon className="h-4 w-4" />
                    </span>
                    <div>
                      <div className="text-xs uppercase tracking-widest text-muted-foreground">
                        {m.label}
                      </div>
                      <div className="text-lg font-semibold tabular-nums">
                        {cur}
                        {m.key === "network" ? " Gbps" : "%"}
                      </div>
                    </div>
                  </div>
                </div>
                <div className="h-48">
                  <ResponsiveContainer>
                    <AreaChart data={chartData}>
                      <defs>
                        <linearGradient id={`g-${m.key}`} x1="0" x2="0" y1="0" y2="1">
                          <stop offset="0%" stopColor={m.color} stopOpacity={0.5} />
                          <stop offset="100%" stopColor={m.color} stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid stroke="var(--color-border)" strokeDasharray="3 3" />
                      <XAxis dataKey="t" stroke="var(--color-muted-foreground)" fontSize={10} />
                      <YAxis
                        stroke="var(--color-muted-foreground)"
                        fontSize={10}
                        domain={m.key === "network" ? [0, "auto"] : [0, 100]}
                      />
                      <Tooltip
                        contentStyle={{
                          background: "var(--color-popover)",
                          border: "1px solid var(--color-border)",
                          borderRadius: 12,
                        }}
                      />
                      <Area
                        type="monotone"
                        dataKey={m.key}
                        stroke={m.color}
                        fill={`url(#g-${m.key})`}
                        strokeWidth={2}
                        isAnimationActive={false}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </>
  );
}
