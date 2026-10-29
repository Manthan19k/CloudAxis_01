import { User, Role } from "./auth";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api/v1";

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in?: number;
  user: User;
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

  async post<T>(path: string, body: any): Promise<T> {
    return this.request<T>(path, {
      method: "POST",
      body: JSON.stringify(body),
    });
  }

  async put<T>(path: string, body: any): Promise<T> {
    return this.request<T>(path, {
      method: "PUT",
      body: JSON.stringify(body),
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
  getSummary: () => api.get<any>("/dashboard/summary"),
  getForecast: () => api.get<any>("/dashboard/forecast"),
};

export const serversApi = {
  list: (skip = 0, limit = 100) => api.get<any>(`/servers/?skip=${skip}&limit=${limit}`),
  get: (id: number) => api.get<any>(`/servers/${id}`),
  create: (body: any) => api.post<any>("/servers/", body),
  update: (id: number, body: any) => api.put<any>(`/servers/${id}`, body),
  delete: (id: number) => api.delete<any>(`/servers/${id}`),
};

export const vmsApi = {
  list: (skip = 0, limit = 100) => api.get<any>(`/vms/?skip=${skip}&limit=${limit}`),
  get: (id: number) => api.get<any>(`/vms/${id}`),
  listByServer: (serverId: number) => api.get<any>(`/vms/server/${serverId}`),
};

export const storageApi = {
  list: (skip = 0, limit = 100) => api.get<any>(`/storage/?skip=${skip}&limit=${limit}`),
  get: (id: number) => api.get<any>(`/storage/${id}`),
};

export const networkApi = {
  list: (skip = 0, limit = 100) => api.get<any>(`/network/?skip=${skip}&limit=${limit}`),
  get: (id: number) => api.get<any>(`/network/${id}`),
};

export const alertsApi = {
  list: (skip = 0, limit = 100) => api.get<any>(`/alerts/?skip=${skip}&limit=${limit}`),
  get: (id: number) => api.get<any>(`/alerts/${id}`),
};

export const inventoryApi = {
  list: (skip = 0, limit = 100) => api.get<any>(`/inventory/?skip=${skip}&limit=${limit}`),
  get: (id: number) => api.get<any>(`/inventory/${id}`),
};
