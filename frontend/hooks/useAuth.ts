"use client";

import { create } from "zustand";
import { User } from "@/types";
import React from "react";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const AUTH_STORAGE_KEY = "auth-storage";

// Safely read auth from localStorage (client-side only)
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

// Safely write auth to localStorage (client-side only)
const writeAuthToStorage = (state: Partial<AuthState>) => {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(
      AUTH_STORAGE_KEY,
      JSON.stringify({ state })
    );
  } catch {}
};

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
    const newState = { accessToken, refreshToken, isLoading: false };
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
    set({ accessToken: access, refreshToken: refresh });
    writeAuthToStorage({ accessToken: access, refreshToken: refresh });
  },
  setUser: (user) => set({ user, isLoading: false }),
  setLoading: (loading) => set({ isLoading: loading }),
  setTempToken: (token) => set({ tempToken: token }),
  clearTempToken: () => set({ tempToken: null }),

  // Call in useEffect to restore tokens from localStorage
  hydrate: () => {
    const stored = readAuthFromStorage();
    if (stored.accessToken || stored.refreshToken) {
      set({ ...stored, isLoading: false });
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
