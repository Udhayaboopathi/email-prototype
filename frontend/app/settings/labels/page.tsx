"use client";


export const dynamic = 'force-dynamic';
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

export default function LabelsSettingsPage() {
  const token = getAccessToken();
  const { data } = useQuery({ queryKey: ["labels"], queryFn: async () => (token ? api.listLabels(token) : []), enabled: Boolean(token) });

  return (
    <main className="space-y-4 p-4 md:p-6">
      <h1 className="text-xl font-semibold text-slate-900 dark:text-slate-100">Labels</h1>
      <div className="flex flex-wrap gap-2 rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
        {(data ?? []).map((label: any) => (
          <span key={label.id} style={{ backgroundColor: label.color }} className="rounded-full px-3 py-1 text-xs font-medium text-white">{label.name}</span>
        ))}
      </div>
    </main>
  );
}