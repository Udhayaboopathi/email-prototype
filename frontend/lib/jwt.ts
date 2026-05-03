/**
 * Safely decodes a JWT's payload section.
 * JWT uses base64url encoding (RFC 4648 §5): uses - and _ instead of + and /,
 * and no padding. The native atob() needs standard base64 with padding.
 */
export function parseJwt(token: string): Record<string, unknown> {
  try {
    const base64url = token.split(".")[1];
    if (!base64url) return {};
    // base64url → standard base64
    const base64 = base64url.replace(/-/g, "+").replace(/_/g, "/");
    // Restore padding so atob() doesn't throw
    const padded = base64.padEnd(base64.length + (4 - (base64.length % 4)) % 4, "=");
    return JSON.parse(atob(padded));
  } catch {
    return {};
  }
}

/** Returns the role string embedded in the JWT, or null if missing/invalid. */
export function getRoleFromToken(token: string): string | null {
  const payload = parseJwt(token);
  const role = payload.role;
  return typeof role === "string" ? role : null;
}
