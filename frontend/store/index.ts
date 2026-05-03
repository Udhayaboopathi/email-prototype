"use client";

import { create } from "zustand";
import { MailItem } from "@/types";

interface UIState {
  // Dark mode
  darkMode: boolean;
  isDarkMode: boolean;
  toggleDarkMode: () => void;

  // Sidebar
  isSidebarCollapsed: boolean;
  toggleSidebar: () => void;
  selectedFolder: string;
  setSelectedFolder: (folder: string) => void;

  // Compose
  composeOpen: boolean;
  setComposeOpen: (open: boolean) => void;

  // Loading
  isLoading: boolean;
  setLoading: (loading: boolean) => void;

  // Mail cache
  cachedMail: Record<string, MailItem[]>;
  setCachedMail: (folder: string, items: MailItem[]) => void;

  // Hydration helper
  hydrate: () => void;
}

export const useUIStore = create<UIState>()((set) => ({
  darkMode: false,
  isDarkMode: false,
  toggleDarkMode: () => {
    set((state) => {
      const newDark = !state.darkMode;
      // Persist to localStorage on client side only
      if (typeof window !== "undefined") {
        localStorage.setItem("darkMode", String(newDark));
      }
      return { darkMode: newDark, isDarkMode: newDark };
    });
  },

  isSidebarCollapsed: false,
  toggleSidebar: () =>
    set((state) => ({ isSidebarCollapsed: !state.isSidebarCollapsed })),

  selectedFolder: "INBOX",
  setSelectedFolder: (folder: string) => set({ selectedFolder: folder }),

  composeOpen: false,
  setComposeOpen: (open: boolean) => set({ composeOpen: open }),

  isLoading: false,
  setLoading: (loading: boolean) => set({ isLoading: loading }),

  cachedMail: {},
  setCachedMail: (folder: string, items: MailItem[]) =>
    set((state) => ({
      cachedMail: { ...state.cachedMail, [folder]: items },
    })),

  // Call hydrate() in a useEffect on the client to restore persisted state
  hydrate: () => {
    if (typeof window !== "undefined") {
      const storedDark = localStorage.getItem("darkMode") === "true";
      set({ darkMode: storedDark, isDarkMode: storedDark });
    }
  },
}));

// Aliases for backward compatibility
export const useAppStore = useUIStore;
