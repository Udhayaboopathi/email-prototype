"use client";


export const dynamic = 'force-dynamic';
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

export default function WebhooksSettingsPage() {
  const token = getAccessToken();
  const { data } = useQuery({ queryKey: ["webhooks"], queryFn: async () => (token ? api.listWebhooks(token) : []), enabled: Boolean(token) });

  return (
    <main className="space-y-4 p-4 md:p-6">
      <h1 className="text-xl font-semibold text-slate-900 dark:text-slate-100">Webhooks</h1>
      <ul className="space-y-2 rounded-xl border border-slate-200 bg-white p-4 text-sm dark:border-slate-800 dark:bg-slate-900">
        {(data ?? []).map((hook: any) => (
          <li key={hook.id} className="text-slate-700 dark:text-slate-200">{hook.url}</li>
        ))}
      </ul>
    </main>
  );
}