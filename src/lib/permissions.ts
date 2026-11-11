import { useAuth } from "@/lib/auth";

export type RoleType = "admin" | "engineer" | "manager" | "viewer" | string;

export type PermissionAction =
  | "manage_users"
  | "manage_roles"
  | "manage_settings"
  | "provision_infrastructure"
  | "manage_inventory"
  | "ack_alerts"
  | "create_alerts"
  | "ingest_monitoring"
  | "view_admin"
  | "view_infrastructure"
  | "view_operations";

const ROLE_PERMISSIONS: Record<string, PermissionAction[]> = {
  admin: [
    "manage_users",
    "manage_roles",
    "manage_settings",
    "provision_infrastructure",
    "manage_inventory",
    "ack_alerts",
    "create_alerts",
    "ingest_monitoring",
    "view_admin",
    "view_infrastructure",
    "view_operations",
  ],
  engineer: [
    "provision_infrastructure",
    "manage_inventory",
    "ack_alerts",
    "create_alerts",
    "ingest_monitoring",
    "view_infrastructure",
    "view_operations",
  ],
  manager: [
    "ack_alerts",
    "view_infrastructure",
    "view_operations",
  ],
  viewer: [
    "view_infrastructure",
    "view_operations",
  ],
};

export function normalizeRole(role: string | null | undefined): string {
  if (!role) return "viewer";
  return role.trim().toLowerCase();
}

export function hasPermission(role: string | null | undefined, action: PermissionAction): boolean {
  const norm = normalizeRole(role);
  const permissions = ROLE_PERMISSIONS[norm] ?? ROLE_PERMISSIONS["viewer"];
  return permissions.includes(action);
}

export function isAdmin(role: string | null | undefined): boolean {
  return normalizeRole(role) === "admin";
}

export function canProvision(role: string | null | undefined): boolean {
  return hasPermission(role, "provision_infrastructure");
}

export function canAckAlerts(role: string | null | undefined): boolean {
  return hasPermission(role, "ack_alerts");
}

export function canManageUsers(role: string | null | undefined): boolean {
  return hasPermission(role, "manage_users");
}

export function canManageInventory(role: string | null | undefined): boolean {
  return hasPermission(role, "manage_inventory");
}

export function usePermissions() {
  const { user } = useAuth();
  const role = normalizeRole(user?.role);

  return {
    role,
    isAdmin: role === "admin",
    isEngineer: role === "engineer",
    isManager: role === "manager",
    isViewer: role === "viewer",
    canManageUsers: hasPermission(role, "manage_users"),
    canManageRoles: hasPermission(role, "manage_roles"),
    canManageSettings: hasPermission(role, "manage_settings"),
    canProvision: hasPermission(role, "provision_infrastructure"),
    canAckAlerts: hasPermission(role, "ack_alerts"),
    canManageInventory: hasPermission(role, "manage_inventory"),
    hasPermission: (action: PermissionAction) => hasPermission(role, action),
  };
}
