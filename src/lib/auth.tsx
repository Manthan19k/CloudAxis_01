import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { authApi } from "./api";

export type Role = "Admin" | "Engineer" | "Manager" | "Viewer";
export interface User {
  id: string;
  name: string;
  email: string;
  role: Role;
  avatar?: string;
  department?: string;
}

interface AuthCtx {
  user: User | null;
  isAuthenticated: boolean;
  ready: boolean;
  login: (email: string, password: string, remember?: boolean) => Promise<User>;
  register: (name: string, email: string, password: string) => Promise<User>;
  logout: () => void;
}

const Ctx = createContext<AuthCtx>(null!);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const raw = localStorage.getItem("cloudaxis-user");
    if (raw) {
      try {
        setUser(JSON.parse(raw));
      } catch {}
    }
    setReady(true);
  }, []);

  const persist = (u: User | null, accessToken?: string, refreshToken?: string, remember = true) => {
    setUser(u);
    if (u && remember) {
      localStorage.setItem("cloudaxis-user", JSON.stringify(u));
      if (accessToken) localStorage.setItem("cloudaxis-access-token", accessToken);
      if (refreshToken) localStorage.setItem("cloudaxis-refresh-token", refreshToken);
    } else {
      localStorage.removeItem("cloudaxis-user");
      localStorage.removeItem("cloudaxis-access-token");
      localStorage.removeItem("cloudaxis-refresh-token");
    }
  };

  const login: AuthCtx["login"] = async (email, password, remember = true) => {
    try {
      const tokens = await authApi.login({ email, password });
      localStorage.setItem("cloudaxis-access-token", tokens.access_token);
      localStorage.setItem("cloudaxis-refresh-token", tokens.refresh_token);
      
      const u = await authApi.me();
      persist(u, tokens.access_token, tokens.refresh_token, remember);
      return u;
    } catch (error) {
      console.error("Login failed:", error);
      throw error;
    }
  };

  const register: AuthCtx["register"] = async (name, email, password) => {
    try {
      // Default role for registration
      const role_name = email.startsWith("admin") ? "admin" : "engineer";
      const u = await authApi.register({ name, email, password, role_name });
      return u;
    } catch (error) {
      console.error("Registration failed:", error);
      throw error;
    }
  };

  const logout = async () => {
    const refreshToken = localStorage.getItem("cloudaxis-refresh-token");
    if (refreshToken) {
      try {
        await authApi.logout({ refresh_token: refreshToken });
      } catch (error) {
        console.error("Logout failed:", error);
      }
    }
    persist(null);
  };

  return (
    <Ctx.Provider value={{ user, isAuthenticated: !!user, ready, login, register, logout }}>
      {children}
    </Ctx.Provider>
  );
}

export const useAuth = () => useContext(Ctx);
