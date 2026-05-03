"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { getRole, roleHome } from "@/lib/auth";

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    const role = getRole();
    if (role) {
      router.replace(roleHome(role));
      return;
    }
    router.replace("/login");
  }, [router]);

  return (
    <main className="grid min-h-screen place-items-center">
      <p className="text-sm text-slate-500 dark:text-slate-400">Redirecting...</p>
    </main>
  );
}
