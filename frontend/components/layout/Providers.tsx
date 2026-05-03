"use client";

import * as React from "react";
import { ThemeProvider as NextThemesProvider } from "next-themes";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/sonner";
import { useAuth } from "@/hooks/useAuth";

type ThemeProviderProps = React.ComponentProps<typeof NextThemesProvider>;

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// ── Auth hydration ────────────────────────────────────────────────────────────
// Restores auth state from localStorage on app boot so isLoading becomes false.
function AuthBootstrap({ children }: { children: React.ReactNode }) {
  const hydrate = useAuth((s) => s.hydrate);

  React.useEffect(() => {
    hydrate();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return <>{children}</>;
}

export function Providers({ children, ...props }: ThemeProviderProps) {
  return (
    <NextThemesProvider {...props}>
      <QueryClientProvider client={queryClient}>
        <AuthBootstrap>
          {children}
          <Toaster />
        </AuthBootstrap>
      </QueryClientProvider>
    </NextThemesProvider>
  );
}
