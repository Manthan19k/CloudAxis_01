import { User, Role } from "./auth";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api/v1";

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in?: number;
  user: User;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  pages: number;
}

export interface Server {
  id: number | string;
  serverId?: string;
  name: string;
  ip: string;
  location: string;
  rack?: string;
  os?: string;
  cpu: number;
  memory: number;
  storage: number;
  temperature: number;
  status: "healthy" | "warning" | "critical" | "offline" | string;
  owner?: string;
  department?: string;
  vmCount: number;
  uptimeDays: number;
}

export interface VM {
  id: number | string;
  vmId?: string;
  name: string;
  host?: string;
  hostName?: string;
  hostId?: number;
  os?: string;
  vCPU: number;
  memoryGB: number;
  diskGB: number;
  cpu: number;
  memory: number;
  status: "healthy" | "warning" | "critical" | "offline" | string;
  ip?: string;
  owner?: string;
  department?: string;
  snapshots: number;
}

export interface Datastore {
  id: number | string;
  dsId?: string;
  name: string;
  type: "SSD" | "NVMe" | "HDD" | "Hybrid" | string;
  capacityTB: number;
  usedTB: number;
  freeTB?: number;
  utilizationPct?: number;
  status: "healthy" | "warning" | "critical" | "offline" | string;
  location?: string;
}

export interface NetworkDevice {
  id: number | string;
  devId?: string;
  name: string;
  type: "Switch" | "Router" | "Firewall" | "Load Balancer" | string;
  vendor?: string;
  ip?: string;
  throughputGbps: number;
  latencyMs: number;
  packetLoss: number;
  status: "healthy" | "warning" | "critical" | "offline" | string;
}

export interface Alert {
  id: number | string;
  alertId?: string;
  severity: "critical" | "warning" | "info" | string;
  title: string;
  source?: string;
  assignee?: string;
  time?: string;
  triggeredAt?: string;
  acknowledged: boolean;
  resolved: boolean;
}

export interface InventoryItem {
  id: number | string;
  invId?: string;
  category: "Server" | "Switch" | "Router" | "Firewall" | "Storage" | "License" | "Software" | string;
  name: string;
  vendor?: string;
  serial?: string;
  purchased?: string;
  purchasedAt?: string;
  warranty?: string;
  warrantyUntil?: string;
  status: "Active" | "Retired" | "In Stock" | string;
}

export interface MetricSample {
  id: number;
  source: string;
  metric: string;
  value: number;
  unit?: string;
  recordedAt?: string;
}

export interface DashboardSummary {
  healthScore: number;
  totalServers: number;
  healthyServers: number;
  totalVms: number;
  healthyVms: number;
  totalDatastores: number;
  totalStorageTb: number;
  usedStorageTb: number;
  storageUtilizationPct: number;
  totalNetworkDevices: number;
  totalAlerts: number;
  unresolvedAlerts: number;
  criticalAlerts: number;
  totalInventory: number;
  activeInventory: number;
}

export interface CapacityForecastPoint {
  month: string;
  servers: number;
  vms: number;
  storage: number;
}

export interface CapacityForecastResponse {
  forecast: CapacityForecastPoint[];
}

class ApiClient {
  private getHeaders() {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    const token = localStorage.getItem("cloudaxis-access-token");
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
  }

  private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${path}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "An error occurred" }));
      const message = error.detail || error.message || "An error occurred";

      // If unauthorized on protected routes (not login attempt), clear stored tokens
      if (response.status === 401 && path !== "/auth/login") {
        localStorage.removeItem("cloudaxis-access-token");
        localStorage.removeItem("cloudaxis-user");
        localStorage.removeItem("cloudaxis-refresh-token");
      }

      throw new Error(message);
    }

    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  async get<T>(path: string): Promise<T> {
    return this.request<T>(path, { method: "GET" });
  }

  async post<T>(path: string, body?: any): Promise<T> {
    return this.request<T>(path, {
      method: "POST",
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  }

  async put<T>(path: string, body?: any): Promise<T> {
    return this.request<T>(path, {
      method: "PUT",
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  }

  async delete<T>(path: string): Promise<T> {
    return this.request<T>(path, { method: "DELETE" });
  }
}

export const api = new ApiClient();

// Domain specific API calls
export const authApi = {
  login: (body: any) => api.post<TokenPair>("/auth/login", body),
  register: (body: any) => api.post<TokenPair>("/auth/register", body),
  me: () => api.get<User>("/auth/me"),
  logout: (body: any) => api.post<void>("/auth/logout", body),
};

export const dashboardApi = {
  getSummary: () => api.get<DashboardSummary>("/dashboard/summary"),
  getForecast: () => api.get<CapacityForecastResponse>("/dashboard/forecast"),
};

export const serversApi = {
  list: (skip = 0, limit = 100) =>
    api.get<PaginatedResponse<Server>>(`/servers/?skip=${skip}&limit=${limit}`),
  listItems: async (skip = 0, limit = 100) => {
    const res = await api.get<PaginatedResponse<Server>>(`/servers/?skip=${skip}&limit=${limit}`);
    return res.items;
  },
  get: (id: number | string) => api.get<Server>(`/servers/${id}`),
  create: (body: Partial<Server>) => api.post<Server>("/servers/", body),
  update: (id: number | string, body: Partial<Server>) => api.put<Server>(`/servers/${id}`, body),
  delete: (id: number | string) => api.delete<void>(`/servers/${id}`),
};

export const vmsApi = {
  list: (skip = 0, limit = 100) =>
    api.get<PaginatedResponse<VM>>(`/vms/?skip=${skip}&limit=${limit}`),
  listItems: async (skip = 0, limit = 100) => {
    const res = await api.get<PaginatedResponse<VM>>(`/vms/?skip=${skip}&limit=${limit}`);
    return res.items;
  },
  get: (id: number | string) => api.get<VM>(`/vms/${id}`),
  create: (body: Partial<VM>) => api.post<VM>("/vms/", body),
  update: (id: number | string, body: Partial<VM>) => api.put<VM>(`/vms/${id}`, body),
  delete: (id: number | string) => api.delete<void>(`/vms/${id}`),
  listByServer: (serverId: number | string, skip = 0, limit = 100) =>
    api.get<PaginatedResponse<VM>>(`/vms/server/${serverId}?skip=${skip}&limit=${limit}`),
};

export const storageApi = {
  list: (skip = 0, limit = 100) =>
    api.get<PaginatedResponse<Datastore>>(`/storage/?skip=${skip}&limit=${limit}`),
  listItems: async (skip = 0, limit = 100) => {
    const res = await api.get<PaginatedResponse<Datastore>>(`/storage/?skip=${skip}&limit=${limit}`);
    return res.items;
  },
  get: (id: number | string) => api.get<Datastore>(`/storage/${id}`),
  create: (body: Partial<Datastore>) => api.post<Datastore>("/storage/", body),
  update: (id: number | string, body: Partial<Datastore>) => api.put<Datastore>(`/storage/${id}`, body),
  delete: (id: number | string) => api.delete<void>(`/storage/${id}`),
};

export const networkApi = {
  list: (skip = 0, limit = 100) =>
    api.get<PaginatedResponse<NetworkDevice>>(`/network/?skip=${skip}&limit=${limit}`),
  listItems: async (skip = 0, limit = 100) => {
    const res = await api.get<PaginatedResponse<NetworkDevice>>(`/network/?skip=${skip}&limit=${limit}`);
    return res.items;
  },
  get: (id: number | string) => api.get<NetworkDevice>(`/network/${id}`),
  create: (body: Partial<NetworkDevice>) => api.post<NetworkDevice>("/network/", body),
  update: (id: number | string, body: Partial<NetworkDevice>) => api.put<NetworkDevice>(`/network/${id}`, body),
  delete: (id: number | string) => api.delete<void>(`/network/${id}`),
};

export const alertsApi = {
  list: (skip = 0, limit = 100) =>
    api.get<PaginatedResponse<Alert>>(`/alerts/?skip=${skip}&limit=${limit}`),
  listItems: async (skip = 0, limit = 100) => {
    const res = await api.get<PaginatedResponse<Alert>>(`/alerts/?skip=${skip}&limit=${limit}`);
    return res.items;
  },
  get: (id: number | string) => api.get<Alert>(`/alerts/${id}`),
  create: (body: Partial<Alert>) => api.post<Alert>("/alerts/", body),
  update: (id: number | string, body: Partial<Alert>) => api.put<Alert>(`/alerts/${id}`, body),
  delete: (id: number | string) => api.delete<void>(`/alerts/${id}`),
  listBySeverity: (severity: string, skip = 0, limit = 100) =>
    api.get<PaginatedResponse<Alert>>(`/alerts/severity/${severity}?skip=${skip}&limit=${limit}`),
};

export const inventoryApi = {
  list: (skip = 0, limit = 100) =>
    api.get<PaginatedResponse<InventoryItem>>(`/inventory/?skip=${skip}&limit=${limit}`),
  listItems: async (skip = 0, limit = 100) => {
    const res = await api.get<PaginatedResponse<InventoryItem>>(`/inventory/?skip=${skip}&limit=${limit}`);
    return res.items;
  },
  get: (id: number | string) => api.get<InventoryItem>(`/inventory/${id}`),
  create: (body: Partial<InventoryItem>) => api.post<InventoryItem>("/inventory/", body),
  update: (id: number | string, body: Partial<InventoryItem>) => api.put<InventoryItem>(`/inventory/${id}`, body),
  delete: (id: number | string) => api.delete<void>(`/inventory/${id}`),
  listByCategory: (category: string, skip = 0, limit = 100) =>
    api.get<PaginatedResponse<InventoryItem>>(`/inventory/category/${category}?skip=${skip}&limit=${limit}`),
};

export const usersApi = {
  list: (skip = 0, limit = 100) => api.get<User[]>(`/users/?skip=${skip}&limit=${limit}`),
  get: (id: number | string) => api.get<User>(`/users/${id}`),
  create: (body: any) => api.post<User>("/users/", body),
  update: (id: number | string, body: any) => api.put<User>(`/users/${id}`, body),
  delete: (id: number | string) => api.delete<void>(`/users/${id}`),
};

export const monitoringApi = {
  create: (body: any) => api.post<MetricSample>("/monitoring/", body),
  listByDevice: (deviceId: string, skip = 0, limit = 100) =>
    api.get<MetricSample[]>(`/monitoring/device/${deviceId}?skip=${skip}&limit=${limit}`),
  getRecent: (hours = 24, skip = 0, limit = 100) =>
    api.get<MetricSample[]>(`/monitoring/recent?hours=${hours}&skip=${skip}&limit=${limit}`),
};
