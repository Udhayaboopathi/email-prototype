"use client";


export const dynamic = 'force-dynamic';
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

export default function ApiKeysSettingsPage() {
  const token = getAccessToken();
  const { data } = useQuery({ queryKey: ["api-keys"], queryFn: async () => (token ? api.listApiKeys(token) : []), enabled: Boolean(token) });

  return (
    <main className="space-y-4 p-4 md:p-6">
      <h1 className="text-xl font-semibold text-slate-900 dark:text-slate-100">API Keys</h1>
      <ul className="space-y-2 rounded-xl border border-slate-200 bg-white p-4 text-sm dark:border-slate-800 dark:bg-slate-900">
        {(data ?? []).map((key: any) => (
          <li key={key.id} className="text-slate-700 dark:text-slate-200">{key.name} ({key.key_prefix}...)</li>
        ))}
      </ul>
    </main>
  );
}