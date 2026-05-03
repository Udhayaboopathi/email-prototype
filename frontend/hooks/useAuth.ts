"use client";

import { create } from "zustand";
import { User, UserRole } from "@/types";
import React from "react";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const AUTH_STORAGE_KEY = "auth-storage";

// ─── JWT helpers ──────────────────────────────────────────────────────────────
function decodeJwtPayload(token: string): Record<string, unknown> {
  try {
    return JSON.parse(atob(token.split(".")[1]));
  } catch {
    return {};
  }
}

function userFromToken(accessToken: string): User | null {
  try {
    const payload = decodeJwtPayload(accessToken);
    if (!payload.sub) return null;
    return {
      id: payload.sub as string,
      email: (payload.email as string) ?? "",
      first_name: (payload.first_name as string) ?? "",
      last_name: (payload.last_name as string) ?? "",
      role: (payload.role as UserRole) ?? "user",
      is_active: true,
      last_login: null,
      domain_id: (payload.domain_id as string) ?? undefined,
      totp_enabled: (payload.totp_enabled as boolean) ?? false,
    };
  } catch {
    return null;
  }
}

// ─── Storage helpers ──────────────────────────────────────────────────────────
const readAuthFromStorage = (): Partial<AuthState> => {
  if (typeof window === "undefined") return {};
  try {
    const raw = window.localStorage.getItem(AUTH_STORAGE_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    return parsed?.state ?? {};
  } catch {
    return {};
  }
};

const writeAuthToStorage = (state: Partial<AuthState>) => {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify({ state }));
  } catch {}
};

// ─── Store ────────────────────────────────────────────────────────────────────
interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  tempToken: string | null;
  isLoading: boolean;
  login: (accessToken: string, refreshToken: string, rememberMe?: boolean) => void;
  logout: () => Promise<void>;
  setTokens: (access: string, refresh: string) => void;
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  setTempToken: (token: string) => void;
  clearTempToken: () => void;
  hydrate: () => void;
}

export const useAuth = create<AuthState>()((set, get) => ({
  user: null,
  accessToken: null,
  refreshToken: null,
  tempToken: null,
  isLoading: true,

  login: (accessToken: string, refreshToken: string, _rememberMe?: boolean) => {
    // Decode JWT to populate user immediately — no extra API call needed
    const user = userFromToken(accessToken);
    const newState = { user, accessToken, refreshToken, isLoading: false };
    set(newState);
    writeAuthToStorage(newState);
  },

  logout: async () => {
    try {
      const token = get().accessToken;
      if (token) {
        await fetch(`${API_URL}/auth/logout`, {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
        });
      }
    } catch (error) {
      console.error("Logout failed", error);
    }
    const cleared = {
      user: null,
      accessToken: null,
      refreshToken: null,
      tempToken: null,
      isLoading: false,
    };
    set(cleared);
    writeAuthToStorage(cleared);
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
  },

  setTokens: (access, refresh) => {
    // Also re-decode user from new token (e.g. after refresh)
    const user = userFromToken(access);
    set({ user, accessToken: access, refreshToken: refresh });
    writeAuthToStorage({ user, accessToken: access, refreshToken: refresh });
  },

  setUser: (user) => set({ user, isLoading: false }),
  setLoading: (loading) => set({ isLoading: loading }),
  setTempToken: (token) => set({ tempToken: token }),
  clearTempToken: () => set({ tempToken: null }),

  hydrate: () => {
    const stored = readAuthFromStorage();
    if (stored.accessToken) {
      // Re-derive user from stored token in case storage was pre-user-field
      const user = stored.user ?? userFromToken(stored.accessToken);
      set({ ...stored, user, isLoading: false });
    } else {
      set({ isLoading: false });
    }
  },
}));

// Hook to initialize auth state on app load
export const useInitializeAuth = () => {
  const { hydrate } = useAuth();
  React.useEffect(() => {
    hydrate();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps
};
