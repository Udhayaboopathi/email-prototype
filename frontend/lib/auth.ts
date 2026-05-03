import { Role, TokenPair } from "@/types";

// Re-export useAuth hook
export { useAuth } from "@/hooks/useAuth";

const ACCESS_KEY = "mail.access_token";
const REFRESH_KEY = "mail.refresh_token";
const ROLE_KEY = "mail.role";

// All localStorage helpers are SSR-safe (guarded by typeof window)

export function setTokens(tokens: TokenPair): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(ACCESS_KEY, tokens.access_token);
  window.localStorage.setItem(REFRESH_KEY, tokens.refresh_token);
}

export function setRole(role: Role): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(ROLE_KEY, role);
}

export function getRole(): Role | null {
  if (typeof window === "undefined") return null;
  const role = window.localStorage.getItem(ROLE_KEY);
  if (role === "super_admin" || role === "domain_admin" || role === "user") {
    return role;
  }
  return null;
}

export function clearTokens(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(ACCESS_KEY);
  window.localStorage.removeItem(REFRESH_KEY);
  window.localStorage.removeItem(ROLE_KEY);
}

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(ACCESS_KEY);
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(REFRESH_KEY);
}

export function roleHome(role: Role): string {
  if (role === "super_admin") return "/super-admin";
  if (role === "domain_admin") return "/domain-admin";
  return "/mail/inbox";
}
