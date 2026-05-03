import { Role, TokenPair, UserRole } from "@/types";

// Re-export useAuth hook so layouts can import from one place
export { useAuth } from "@/hooks/useAuth";

const AUTH_STORAGE_KEY = "auth-storage"; // matches useAuth.ts

// ─── Role helpers (read from Zustand persisted storage) ───────────────────────
// These are used by page.tsx root route and redirectUser() for SSR-safe access.

export function getRole(): Role | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(AUTH_STORAGE_KEY);
    if (!raw) return null;
    const role = JSON.parse(raw)?.state?.user?.role as string | undefined;
    if (role === "super_admin" || role === "domain_admin" || role === "user") {
      return role as Role;
    }
    return null;
  } catch {
    return null;
  }
}

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(AUTH_STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw)?.state?.accessToken ?? null;
  } catch {
    return null;
  }
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(AUTH_STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw)?.state?.refreshToken ?? null;
  } catch {
    return null;
  }
}

export function clearTokens(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(AUTH_STORAGE_KEY);
}

// Kept for legacy callers — no-op since tokens are now stored via useAuth.login()
export function setTokens(_tokens: TokenPair): void {}
export function setRole(_role: Role): void {}

export function roleHome(role: Role | UserRole | undefined | null): string {
  if (role === "super_admin") return "/super-admin";
  if (role === "domain_admin") return "/domain-admin";
  return "/mail/inbox";
}

export function redirectUser(role: Role | UserRole | undefined | null): string {
  return roleHome(role);
}
