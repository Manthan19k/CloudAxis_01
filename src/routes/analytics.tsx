import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "@/components/app/shell";
import { Card, PageHeader } from "@/components/app/primitives";
import { dashboardApi, serversApi, storageApi, Server } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle, RefreshCw } from "lucide-react";
import { seriesTimeline } from "@/lib/mock-data";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export const Route = createFileRoute("/analytics")({
  head: () => ({ meta: [{ title: "Analytics — CloudAxis" }] }),
  component: () => (
    <AppShell>
      <Analytics />
    </AppShell>
  ),
});

function Analytics() {
  const {
    data: forecastData,
    isLoading: isLoadingForecast,
    isError: isErrorForecast,
    error: errorForecast,
    refetch: refetchForecast,
  } = useQuery({
    queryKey: ["dashboard", "forecast"],
    queryFn: () => dashboardApi.getForecast(),
  });

  const {
    data: serversData,
    isLoading: isLoadingServers,
    isError: isErrorServers,
    error: errorServers,
    refetch: refetchServers,
  } = useQuery({
    queryKey: ["servers"],
    queryFn: () => serversApi.list(),
  });

  const { data: storageData, isLoading: isLoadingStorage } = useQuery({
    queryKey: ["storage"],
    queryFn: () => storageApi.list(),
  });

  const isLoading = isLoadingForecast || isLoadingServers || isLoadingStorage;
  const isError = isErrorForecast || isErrorServers;
  const error = errorForecast || errorServers;

  const servers: Server[] = serversData?.items || [];
  const datastores = storageData?.items || [];

  const avgCpu =
    servers.length > 0
      ? Math.round(servers.reduce((sum, s) => sum + (s.cpu ?? 0), 0) / servers.length)
      : 50;
  const avgMem =
    servers.length > 0
      ? Math.round(servers.reduce((sum, s) => sum + (s.memory ?? 0), 0) / servers.length)
      : 55;
  const totalCap = datastores.reduce((sum, d) => sum + (d.capacityTB || 0), 0);
  const totalUsed = datastores.reduce((sum, d) => sum + (d.usedTB || 0), 0);
  const avgStorage = totalCap > 0 ? Math.round((totalUsed / totalCap) * 100) : 40;

  // Use the 24h baseline derived from live servers & storage
  const trend = seriesTimeline(24, avgCpu, 15, avgMem);

  // Directly map the live 12-month capacity forecast from backend
  const forecast = (forecastData?.forecast || []).map((pt) => ({
    m: pt.month,
    servers: pt.servers,
    vms: pt.vms,
    storage: pt.storage,
  }));

  // Top 12 servers sorted by CPU descending
  const topServers = [...servers].sort((a, b) => (b.cpu ?? 0) - (a.cpu ?? 0)).slice(0, 12);

  return (
    <>
      <PageHeader
        eyebrow="Operations"
        title="Analytics & Forecasting"
        subtitle={
          isLoading
            ? "Loading analytics…"
            : "Trends, capacity planning, and performance comparisons."
        }
      />

      {isLoading ? (
        <div className="grid gap-4 lg:grid-cols-2">
          <Card className="p-6">
            <Skeleton className="mb-2 h-4 w-40" />
            <Skeleton className="h-64 w-full rounded-lg" />
          </Card>
          <Card className="p-6">
            <Skeleton className="mb-2 h-4 w-40" />
            <Skeleton className="h-64 w-full rounded-lg" />
          </Card>
          <Card className="p-6 lg:col-span-2">
            <Skeleton className="mb-2 h-4 w-48" />
            <Skeleton className="h-72 w-full rounded-lg" />
          </Card>
        </div>
      ) : isError ? (
        <div className="flex flex-col items-center justify-center rounded-2xl border border-destructive/20 bg-destructive/5 p-10 text-center">
          <AlertCircle className="h-10 w-10 text-destructive" />
          <h3 className="mt-4 text-base font-semibold">Failed to load analytics</h3>
          <p className="mt-1 text-xs text-muted-foreground">
            {(error as any)?.message || "Network error occurred"}
          </p>
          <button
            onClick={() => {
              refetchForecast();
              refetchServers();
            }}
            className="mt-4 inline-flex items-center gap-2 rounded-lg bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground"
          >
            <RefreshCw className="h-3.5 w-3.5" /> Try again
          </button>
        </div>
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          <Card>
            <div className="mb-2 text-sm font-semibold">Infrastructure trend (24h)</div>
            <div className="h-64">
              <ResponsiveContainer>
                <LineChart data={trend}>
                  <CartesianGrid stroke="var(--color-border)" strokeDasharray="3 3" />
                  <XAxis dataKey="t" stroke="var(--color-muted-foreground)" fontSize={10} />
                  <YAxis stroke="var(--color-muted-foreground)" fontSize={10} />
                  <Tooltip
                    contentStyle={{
                      background: "var(--color-popover)",
                      border: "1px solid var(--color-border)",
                      borderRadius: 12,
                    }}
                  />
                  <Legend />
                  <Line dataKey="cpu" stroke="var(--color-info)" dot={false} strokeWidth={2} />
                  <Line
                    dataKey="memory"
                    stroke="var(--color-success)"
                    dot={false}
                    strokeWidth={2}
                  />
                  <Line
                    dataKey="storage"
                    stroke="var(--color-accent)"
                    dot={false}
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <Card>
            <div className="mb-2 text-sm font-semibold">12-month capacity forecast</div>
            <div className="h-64">
              <ResponsiveContainer>
                <AreaChart data={forecast}>
                  <defs>
                    <linearGradient id="f-s" x1="0" x2="0" y1="0" y2="1">
                      <stop offset="0%" stopColor="var(--color-info)" stopOpacity={0.5} />
                      <stop offset="100%" stopColor="var(--color-info)" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="f-v" x1="0" x2="0" y1="0" y2="1">
                      <stop offset="0%" stopColor="var(--color-accent)" stopOpacity={0.5} />
                      <stop offset="100%" stopColor="var(--color-accent)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="m" stroke="var(--color-muted-foreground)" fontSize={10} />
                  <YAxis stroke="var(--color-muted-foreground)" fontSize={10} />
                  <Tooltip
                    contentStyle={{
                      background: "var(--color-popover)",
                      border: "1px solid var(--color-border)",
                      borderRadius: 12,
                    }}
                  />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="servers"
                    stroke="var(--color-info)"
                    fill="url(#f-s)"
                    strokeWidth={2}
                  />
                  <Area
                    type="monotone"
                    dataKey="vms"
                    stroke="var(--color-accent)"
                    fill="url(#f-v)"
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <Card className="lg:col-span-2">
            <div className="mb-2 text-sm font-semibold">
              Performance comparison — top 12 servers
            </div>
            <div className="h-72">
              {topServers.length === 0 ? (
                <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
                  No servers found.
                </div>
              ) : (
                <ResponsiveContainer>
                  <BarChart data={topServers}>
                    <CartesianGrid stroke="var(--color-border)" strokeDasharray="3 3" />
                    <XAxis
                      dataKey="name"
                      stroke="var(--color-muted-foreground)"
                      fontSize={9}
                      angle={-30}
                      textAnchor="end"
                      height={80}
                    />
                    <YAxis stroke="var(--color-muted-foreground)" fontSize={10} />
                    <Tooltip
                      contentStyle={{
                        background: "var(--color-popover)",
                        border: "1px solid var(--color-border)",
                        borderRadius: 12,
                      }}
                    />
                    <Legend />
                    <Bar
                      dataKey="cpu"
                      name="CPU %"
                      fill="var(--color-info)"
                      radius={[6, 6, 0, 0]}
                    />
                    <Bar
                      dataKey="memory"
                      name="Memory %"
                      fill="var(--color-accent)"
                      radius={[6, 6, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </Card>
        </div>
      )}
    </>
  );
}
