import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "@/components/app/shell";
import { PageHeader, StatusPill } from "@/components/app/primitives";
import { DataTable } from "@/components/app/data-table";
import { inventoryApi, InventoryItem } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle, Package, RefreshCw } from "lucide-react";

export const Route = createFileRoute("/inventory")({
  head: () => ({ meta: [{ title: "Inventory — CloudAxis" }] }),
  component: () => (
    <AppShell>
      <Inventory />
    </AppShell>
  ),
});

function Inventory() {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["inventory"],
    queryFn: () => inventoryApi.list(),
  });

  const rows: InventoryItem[] = data?.items || [];

  return (
    <>
      <PageHeader
        eyebrow="Operations"
        title="Asset Inventory"
        subtitle={isLoading ? "Loading tracked assets…" : `${rows.length} tracked assets`}
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
          <h3 className="mt-4 text-base font-semibold">Failed to load inventory</h3>
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
              label: "Asset",
              render: (i) => (
                <div className="flex items-center gap-2">
                  <span className="grid h-8 w-8 place-items-center rounded-lg bg-primary/15 text-primary">
                    <Package className="h-4 w-4" />
                  </span>
                  <div>
                    <div className="font-medium">{i.name}</div>
                    <div className="text-xs text-muted-foreground">{i.serial || "—"}</div>
                  </div>
                </div>
              ),
            },
            { key: "category", label: "Category" },
            { key: "vendor", label: "Vendor", render: (i) => i.vendor || "—" },
            {
              key: "purchased",
              label: "Purchased",
              render: (i) =>
                i.purchased ||
                (i.purchasedAt ? new Date(i.purchasedAt).toISOString().slice(0, 10) : "—"),
            },
            {
              key: "warranty",
              label: "Warranty until",
              render: (i) =>
                i.warranty ||
                (i.warrantyUntil ? new Date(i.warrantyUntil).toISOString().slice(0, 10) : "—"),
            },
            { key: "status", label: "Status", render: (i) => <StatusPill status={i.status} /> },
          ]}
        />
      )}
    </>
  );
}
