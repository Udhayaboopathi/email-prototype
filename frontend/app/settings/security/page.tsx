"use client";


export const dynamic = 'force-dynamic';
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

export default function SecuritySettingsPage() {
  const token = getAccessToken();
  const { data } = useQuery({ queryKey: ["login-activity"], queryFn: async () => (token ? api.getLoginActivity(token) : []), enabled: Boolean(token) });

  return (
    <main className="space-y-4 p-4 md:p-6">
      <h1 className="text-xl font-semibold text-slate-900 dark:text-slate-100">Security</h1>
      <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
        <p className="mb-3 text-sm text-slate-600 dark:text-slate-300">Recent login activity</p>
        <ul className="space-y-2 text-sm text-slate-700 dark:text-slate-200">
          {(data ?? []).map((row: any) => (
            <li key={row.id}>{row.location ?? "Unknown"} - {row.ip_address}</li>
          ))}
        </ul>
      </div>
    </main>
  );
}