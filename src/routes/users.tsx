import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "@/components/app/shell";
import { PageHeader, StatusPill } from "@/components/app/primitives";
import { DataTable } from "@/components/app/data-table";
import { usersApi } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { usePermissions } from "@/lib/permissions";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle, Plus, RefreshCw, Shield, X } from "lucide-react";
import { toast } from "sonner";

export const Route = createFileRoute("/users")({
  head: () => ({ meta: [{ title: "Users — CloudAxis" }] }),
  component: () => (
    <AppShell>
      <Users />
    </AppShell>
  ),
});

export interface UserRow {
  id: number | string;
  name: string;
  email: string;
  role: string;
  department?: string;
  isActive?: boolean;
  active?: boolean;
  is_active?: boolean;
  lastLogin?: string | null;
}

function Users() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const { isAdmin } = usePermissions();
  const [inviting, setInviting] = useState(false);

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["users"],
    queryFn: () => usersApi.list(),
    enabled: isAdmin,
  });

  const toggleAccessMutation = useMutation({
    mutationFn: ({ id, currentActive }: { id: string | number; currentActive: boolean }) =>
      usersApi.update(id, { isActive: !currentActive }),
    onSuccess: (_, vars) => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      toast.success(vars.currentActive ? "Access revoked" : "Access restored");
    },
    onError: (err: any) => {
      toast.error(err.message || "Failed to update user access");
    },
  });

  const inviteMutation = useMutation({
    mutationFn: async (userData: {
      name: string;
      email: string;
      roleName: string;
      password: string;
      department?: string;
    }) => {
      return await usersApi.create(userData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      toast.success("Invitation sent");
      setInviting(false);
    },
    onError: (err: any) => {
      toast.error(err.message || "Failed to invite user");
    },
  });

  if (!isAdmin) {
    return (
      <div className="flex flex-col items-center justify-center rounded-2xl border border-destructive/20 bg-destructive/5 p-12 text-center">
        <Shield className="h-12 w-12 text-destructive" />
        <h3 className="mt-4 text-base font-semibold">Access Denied</h3>
        <p className="mt-1 max-w-sm text-xs text-muted-foreground">
          Administrator privileges are required to view and manage user accounts.
        </p>
      </div>
    );
  }

  const rows: UserRow[] = (data as any) || [];

  return (
    <>
      <PageHeader
        eyebrow="Administration"
        title="User Management"
        subtitle={isLoading ? "Loading users…" : `${rows.length} users registered`}
        actions={
          <button
            onClick={() => setInviting(true)}
            className="inline-flex items-center gap-1.5 rounded-md bg-primary px-3 py-2 text-xs font-medium text-primary-foreground"
          >
            <Plus className="h-3.5 w-3.5" /> Invite user
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
          <h3 className="mt-4 text-base font-semibold">Failed to load users</h3>
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
              label: "User",
              render: (u) => (
                <div className="flex items-center gap-2">
                  <span className="grid h-8 w-8 place-items-center rounded-full bg-gradient-to-br from-info to-accent text-xs font-semibold text-primary-foreground">
                    {u.name
                      ? u.name
                          .split(" ")
                          .map((n) => n[0])
                          .join("")
                      : "U"}
                  </span>
                  <div>
                    <div className="font-medium">{u.name}</div>
                    <div className="text-xs text-muted-foreground">{u.email}</div>
                  </div>
                </div>
              ),
            },
            {
              key: "role",
              label: "Role",
              render: (u) => (
                <span className="text-xs font-medium capitalize text-foreground">{u.role}</span>
              ),
            },
            {
              key: "status",
              label: "Status",
              render: (u) => {
                const active = u.isActive ?? u.active ?? u.is_active ?? true;
                return <StatusPill status={active ? "healthy" : "offline"} />;
              },
            },
            { key: "department", label: "Department", render: (u) => u.department || "General" },
            {
              key: "lastLogin",
              label: "Last login",
              render: (u) =>
                u.lastLogin
                  ? new Date(u.lastLogin).toLocaleDateString([], {
                      year: "numeric",
                      month: "short",
                      day: "numeric",
                    })
                  : "Never",
            },
            {
              key: "active",
              label: "Access",
              render: (u) => {
                const active = u.isActive ?? u.active ?? u.is_active ?? true;
                const isSelf = String(u.id) === String(user?.id) || u.email?.toLowerCase() === user?.email?.toLowerCase();
                return (
                  <button
                    disabled={toggleAccessMutation.isPending || (active && isSelf)}
                    title={active && isSelf ? "You cannot deactivate your own account" : undefined}
                    onClick={() =>
                      toggleAccessMutation.mutate({ id: u.id, currentActive: active })
                    }
                    className={`rounded-md border border-border px-2 py-1 text-xs hover:text-foreground disabled:opacity-50 ${
                      active && isSelf ? "cursor-not-allowed opacity-40 text-muted-foreground" : ""
                    }`}
                  >
                    {active ? "Disable" : "Enable"}
                  </button>
                );
              },
            },
          ]}
        />
      )}

      {inviting ? (
        <InviteForm
          onClose={() => setInviting(false)}
          isSubmitting={inviteMutation.isPending}
          onSave={(formData) => inviteMutation.mutate(formData)}
        />
      ) : null}
    </>
  );
}

function InviteForm({
  onClose,
  onSave,
  isSubmitting,
}: {
  onClose: () => void;
  onSave: (u: { name: string; email: string; roleName: string; password: string; department?: string }) => void;
  isSubmitting?: boolean;
}) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("Engineer");

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-background/70 p-4 backdrop-blur" onClick={onClose}>
      <div className="w-full max-w-md rounded-2xl border border-border bg-popover p-6 shadow-card" onClick={(e) => e.stopPropagation()}>
        <div className="mb-4 flex items-center justify-between">
          <div className="text-lg font-semibold">Invite user</div>
          <button onClick={onClose} className="rounded-md p-1 text-muted-foreground hover:text-foreground">
            <X className="h-4 w-4" />
          </button>
        </div>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (name.trim().length < 2) return toast.error("Name must be at least 2 characters");
            if (!email.includes("@")) return toast.error("Enter a valid email");
            if (password.length < 8) return toast.error("Password must be at least 8 characters");
            onSave({
              name: name.trim(),
              email: email.trim(),
              password,
              roleName: role.toLowerCase(),
              department: "General",
            });
          }}
          className="space-y-3"
        >
          <div>
            <label className="mb-1.5 block text-xs font-medium text-muted-foreground">Name</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Alex Chen"
              className="w-full rounded-lg border border-border bg-input p-2 text-sm outline-none"
            />
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-medium text-muted-foreground">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="e.g. alex@cloudaxis.com"
              className="w-full rounded-lg border border-border bg-input p-2 text-sm outline-none"
            />
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-medium text-muted-foreground">Temporary password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Minimum 8 characters"
              className="w-full rounded-lg border border-border bg-input p-2 text-sm outline-none"
            />
            <span className="mt-1 block text-[11px] text-muted-foreground">
              Must be at least 8 characters
            </span>
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-medium text-muted-foreground">Role</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full rounded-lg border border-border bg-input p-2 text-sm"
            >
              {["Admin", "Engineer", "Manager", "Viewer"].map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </div>
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground disabled:opacity-50"
          >
            {isSubmitting ? "Inviting…" : "Send invitation"}
          </button>
        </form>
      </div>
    </div>
  );
}
