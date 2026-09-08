import { createContext, useContext, useState, ReactNode, useEffect } from "react";
import api from "../api/client";

interface AuthCtx {
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const Ctx = createContext<AuthCtx | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem("pp_token"));

  useEffect(() => {
    if (token) localStorage.setItem("pp_token", token);
    else localStorage.removeItem("pp_token");
  }, [token]);

  async function login(email: string, password: string) {
    const form = new URLSearchParams({ username: email, password });
    const { data } = await api.post("/api/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" }
    });
    setToken(data.access_token);
  }

  async function register(email: string, password: string) {
    await api.post("/api/auth/register", { email, password });
    await login(email, password);
  }

  function logout() {
    setToken(null);
  }

  return <Ctx.Provider value={{ token, login, register, logout }}>{children}</Ctx.Provider>;
}

export function useAuth() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useAuth outside provider");
  return ctx;
}
