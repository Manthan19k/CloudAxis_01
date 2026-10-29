import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { authApi } from "./api";

export type Role = "admin" | "engineer" | "manager" | "viewer" | string;
export interface User {
  id: number | string;
  name: string;
  email: string;
  role: string;
  avatar?: string;
  department?: string;
  is_active?: boolean;
}

interface AuthCtx {
  user: User | null;
  isAuthenticated: boolean;
  ready: boolean;
  login: (email: string, password: string, remember?: boolean) => Promise<User>;
  register: (name: string, email: string, password: string) => Promise<User>;
  logout: () => Promise<void>;
}

const Ctx = createContext<AuthCtx>(null!);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);

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

  useEffect(() => {
    let active = true;

    async function initSession() {
      const token = localStorage.getItem("cloudaxis-access-token");
      const rawUser = localStorage.getItem("cloudaxis-user");

      if (rawUser) {
        try {
          const parsed = JSON.parse(rawUser);
          if (active) setUser(parsed);
        } catch {
          // ignore corrupted local state
        }
      }

      if (token) {
        try {
          const freshUser = await authApi.me();
          if (active) {
            setUser(freshUser);
            localStorage.setItem("cloudaxis-user", JSON.stringify(freshUser));
          }
        } catch (error) {
          console.warn("Session restore failed, clearing auth state:", error);
          if (active) {
            persist(null);
          }
        }
      } else {
        if (active) {
          persist(null);
        }
      }

      if (active) {
        setReady(true);
      }
    }

    initSession();

    return () => {
      active = false;
    };
  }, []);

  const login: AuthCtx["login"] = async (email, password, remember = true) => {
    try {
      const tokens = await authApi.login({ email: email.trim().toLowerCase(), password, remember });
      persist(tokens.user, tokens.access_token, tokens.refresh_token, remember);
      return tokens.user;
    } catch (error) {
      console.error("Login failed:", error);
      throw error;
    }
  };

  const register: AuthCtx["register"] = async (name, email, password) => {
    try {
      const cleanEmail = email.trim().toLowerCase();
      const role_name = cleanEmail.startsWith("admin") ? "admin" : "engineer";
      const tokens = await authApi.register({ name: name.trim(), email: cleanEmail, password, role_name });
      persist(tokens.user, tokens.access_token, tokens.refresh_token, true);
      return tokens.user;
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
        console.error("Logout request failed:", error);
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
