"use client";

import { useAuth } from "@/hooks/useAuth";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { UserRole } from "@/types";

interface RoleGuardProps {
  allowedRoles: UserRole[];
  children: React.ReactNode;
  fallbackUrl?: string;
}

export function RoleGuard({
  allowedRoles,
  children,
  fallbackUrl = "/login",
}: RoleGuardProps) {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isLoading) {
      return; // Wait for user data to be loaded
    }

    if (!user) {
      router.push(fallbackUrl);
      return;
    }

    if (!allowedRoles.includes(user.role)) {
      // Redirect based on role if not allowed
      const homeUrl =
        user.role === "super_admin"
          ? "/super-admin"
          : user.role === "domain_admin"
            ? "/domain-admin"
            : "/mail";
      router.push(homeUrl);
    }
  }, [user, isLoading, allowedRoles, router, fallbackUrl]);

  if (isLoading || !user || !allowedRoles.includes(user.role)) {
    // You can render a loading spinner here
    return <div>Loading...</div>;
  }

  return <>{children}</>;
}
