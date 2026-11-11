import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "@/components/app/shell";
import { Card, PageHeader } from "@/components/app/primitives";
import { usersApi, User } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { usePermissions } from "@/lib/permissions";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Skeleton } from "@/components/ui/skeleton";
import {
  AlertCircle,
  Check,
  RefreshCw,
  Shield,
  ShieldAlert,
  ShieldCheck,
  UserCheck,
  Users as UsersIcon,
  X,
} from "lucide-react";
import { toast } from "sonner";

export const Route = createFileRoute("/roles")({
  head: () => ({ meta: [{ title: "Roles & Permissions — CloudAxis" }] }),
  component: () => (
    <AppShell>
      <Roles />
    </AppShell>
  ),
});

interface RoleDefinition {
  name: string;
  key: "admin" | "engineer" | "manager" | "viewer";
  desc: string;
  badgeColor: string;
  perms: boolean[];
}

const ROLE_DEFINITIONS: RoleDefinition[] = [
  {
    name: "Admin",
    key: "admin",
    desc: "Full administrative access — user management, role assignments, system settings, and infrastructure operations.",
    badgeColor: "bg-destructive/15 text-destructive border-destructive/20",
    perms: [true, true, true, true, true, true],
  },
  {
    name: "Engineer",
    key: "engineer",
    desc: "Infrastructure provisioning and operational management — create/modify/delete servers, VMs, storage, and network devices.",
    badgeColor: "bg-info/15 text-info border-info/20",
    perms: [true, true, true, true, false, false],
  },
  {
    name: "Manager",
    key: "manager",
    desc: "Operational oversight — view all infrastructure, analyze monitoring and reports, and acknowledge or resolve alerts.",
    badgeColor: "bg-accent/15 text-accent border-accent/20",
    perms: [true, false, true, true, false, false],
  },
  {
    name: "Viewer",
    key: "viewer",
    desc: "Read-only console visibility across dashboards, topology, inventory, and telemetry without mutation privileges.",
    badgeColor: "bg-muted text-muted-foreground border-border",
    perms: [true, false, false, false, false, false],
  },
];

const CAPABILITIES = [
  "View console & dashboards",
  "Provision & manage infrastructure",
  "Acknowledge & resolve alerts",
  "Generate operational reports",
  "Manage system settings",
  "Manage users & roles",
];

function Roles() {
  const queryClient = useQueryClient();
  const { user: currentUser } = useAuth();
  const { isAdmin } = usePermissions();
  const [selectedUser, setSelectedUser] = useState<string>("");
  const [targetRole, setTargetRole] = useState<string>("engineer");

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["users"],
    queryFn: () => usersApi.list(),
    enabled: isAdmin,
  });

  const updateRoleMutation = useMutation({
    mutationFn: ({ userId, roleName }: { userId: string | number; roleName: string }) =>
      usersApi.update(userId, { roleName }),
    onSuccess: (_, vars) => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      toast.success(`Role updated successfully to ${vars.roleName}`);
      setSelectedUser("");
    },
    onError: (err: any) => {
      toast.error(err.message || "Failed to update user role");
    },
  });

  if (!isAdmin) {
    return (
      <div className="flex flex-col items-center justify-center rounded-2xl border border-destructive/20 bg-destructive/5 p-12 text-center">
        <ShieldAlert className="h-12 w-12 text-destructive" />
        <h3 className="mt-4 text-base font-semibold">Access Denied</h3>
        <p className="mt-1 max-w-sm text-xs text-muted-foreground">
          Administrator privileges are required to view role configurations and manage role assignments.
        </p>
      </div>
    );
  }

  const users: User[] = (data as any) || [];
  const activeAdmins = users.filter(
    (u) => (u.role || "").toLowerCase() === "admin" && (u.is_active ?? true)
  );

  return (
    <>
      <PageHeader
        eyebrow="Administration"
        title="Roles & Permissions"
        subtitle={
          isLoading
            ? "Loading role assignments…"
            : `${users.length} users assigned across 4 access tiers`
        }
      />

      {isLoading ? (
        <div className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {[1, 2, 3, 4].map((i) => (
              <Card key={i} className="p-5">
                <Skeleton className="h-6 w-24 mb-2" />
                <Skeleton className="h-4 w-full mb-4" />
                <Skeleton className="h-8 w-16" />
              </Card>
            ))}
          </div>
          <Card className="p-6">
            <Skeleton className="h-8 w-48 mb-4" />
            <Skeleton className="h-32 w-full" />
          </Card>
        </div>
      ) : isError ? (
        <div className="flex flex-col items-center justify-center rounded-2xl border border-destructive/20 bg-destructive/5 p-10 text-center">
          <AlertCircle className="h-10 w-10 text-destructive" />
          <h3 className="mt-4 text-base font-semibold">Failed to load roles and users</h3>
          <p className="mt-1 text-xs text-muted-foreground">
            {(error as any)?.message || "A network or server error occurred."}
          </p>
          <button
            onClick={() => refetch()}
            className="mt-4 inline-flex items-center gap-2 rounded-lg bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground"
          >
            <RefreshCw className="h-3.5 w-3.5" /> Try again
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Role Summary Cards with Dynamic User Counts */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {ROLE_DEFINITIONS.map((r) => {
              const assigned = users.filter(
                (u) => (u.role || "").toLowerCase() === r.key
              );
              return (
                <Card key={r.key} className="flex flex-col justify-between p-5">
                  <div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="grid h-8 w-8 place-items-center rounded-lg bg-accent/15 text-accent">
                          <Shield className="h-4 w-4" />
                        </span>
                        <span className="font-semibold">{r.name}</span>
                      </div>
                      <span
                        className={`rounded-full border px-2 py-0.5 text-[11px] font-medium ${r.badgeColor}`}
                      >
                        {assigned.length} {assigned.length === 1 ? "user" : "users"}
                      </span>
                    </div>
                    <p className="mt-3 text-xs leading-relaxed text-muted-foreground">
                      {r.desc}
                    </p>
                  </div>

                  <div className="mt-4 border-t border-border pt-3">
                    <div className="text-[11px] font-medium text-muted-foreground">Assigned members:</div>
                    <div className="mt-1.5 flex flex-wrap gap-1">
                      {assigned.length === 0 ? (
                        <span className="text-[11px] italic text-muted-foreground/60">No users</span>
                      ) : (
                        assigned.slice(0, 4).map((u) => (
                          <span
                            key={u.id}
                            className="inline-flex items-center rounded-md bg-secondary px-1.5 py-0.5 text-[10px] font-medium"
                            title={u.email}
                          >
                            {u.name}
                          </span>
                        ))
                      )}
                      {assigned.length > 4 ? (
                        <span className="text-[10px] text-muted-foreground">
                          +{assigned.length - 4} more
                        </span>
                      ) : null}
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>

          {/* Interactive Role Reassignment Section */}
          <Card className="p-5">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold flex items-center gap-2">
                  <UserCheck className="h-4 w-4 text-primary" />
                  Assign User Role
                </h3>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Update an account's security authorization tier across the platform.
                </p>
              </div>
            </div>

            <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
              <div className="flex-1">
                <label className="mb-1 block text-xs font-medium text-muted-foreground">Select User</label>
                <select
                  value={selectedUser}
                  onChange={(e) => {
                    const uid = e.target.value;
                    setSelectedUser(uid);
                    const found = users.find((u) => String(u.id) === uid);
                    if (found?.role) {
                      setTargetRole(found.role.toLowerCase());
                    }
                  }}
                  className="w-full rounded-lg border border-border bg-input p-2 text-xs"
                >
                  <option value="">Choose a user to reassign…</option>
                  {users.map((u) => (
                    <option key={u.id} value={u.id}>
                      {u.name} ({u.email}) — current: {u.role}
                    </option>
                  ))}
                </select>
              </div>

              <div className="w-full sm:w-48">
                <label className="mb-1 block text-xs font-medium text-muted-foreground">Target Role</label>
                <select
                  value={targetRole}
                  onChange={(e) => setTargetRole(e.target.value)}
                  disabled={!selectedUser}
                  className="w-full rounded-lg border border-border bg-input p-2 text-xs disabled:opacity-50"
                >
                  {ROLE_DEFINITIONS.map((r) => (
                    <option key={r.key} value={r.key}>
                      {r.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="sm:self-end">
                <button
                  disabled={!selectedUser || updateRoleMutation.isPending}
                  onClick={() => {
                    if (!selectedUser) return;
                    const targetObj = users.find((u) => String(u.id) === selectedUser);
                    if (!targetObj) return;

                    // Last admin safeguard
                    const isDemotingAdmin =
                      (targetObj.role || "").toLowerCase() === "admin" &&
                      targetRole.toLowerCase() !== "admin";
                    if (isDemotingAdmin && activeAdmins.length <= 1) {
                      toast.error("Cannot reassign the last active administrator.");
                      return;
                    }

                    updateRoleMutation.mutate({
                      userId: selectedUser,
                      roleName: targetRole.toLowerCase(),
                    });
                  }}
                  className="w-full sm:w-auto inline-flex items-center justify-center gap-1.5 rounded-lg bg-primary px-4 py-2 text-xs font-medium text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50"
                >
                  {updateRoleMutation.isPending ? "Updating…" : "Apply Role"}
                </button>
              </div>
            </div>
          </Card>

          {/* Permissions & Capabilities Matrix */}
          <Card>
            <div className="p-4 border-b border-border">
              <h3 className="text-sm font-semibold flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-accent" />
                Access Tier Capability Matrix
              </h3>
              <p className="text-xs text-muted-foreground mt-0.5">
                Exact backend and frontend permission boundaries enforced per role.
              </p>
            </div>
            <div className="overflow-x-auto p-4">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs uppercase tracking-widest text-muted-foreground">
                    <th className="py-3">Platform Capability</th>
                    {ROLE_DEFINITIONS.map((r) => (
                      <th key={r.name} className="py-3 text-center">
                        <div className="inline-flex items-center gap-1.5">
                          <Shield className="h-3.5 w-3.5" />
                          {r.name}
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {CAPABILITIES.map((cap, i) => (
                    <tr key={cap} className="border-t border-border">
                      <td className="py-3 font-medium text-xs">{cap}</td>
                      {ROLE_DEFINITIONS.map((r) => (
                        <td key={r.name} className="py-3 text-center">
                          {r.perms[i] ? (
                            <Check className="mx-auto h-4 w-4 text-success" />
                          ) : (
                            <X className="mx-auto h-4 w-4 text-muted-foreground/40" />
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}
    </>
  );
}
