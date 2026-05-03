"use client";

import { useQuery } from "@tanstack/react-query";
import { getAccessToken } from "@/lib/auth";
import { api } from "@/lib/api";

export default function DomainAdminSharedMailboxesPage() {
  const token = getAccessToken();
  const { data } = useQuery({
    queryKey: ["shared-mailboxes"],
    queryFn: async () => (token ? api.getSharedMailboxes(token) : []),
    enabled: Boolean(token)
  });

  return (
    <main className="space-y-4 p-4 md:p-6">
      <h1 className="text-xl font-semibold text-slate-900 dark:text-slate-100">Shared Mailboxes</h1>
      <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
        {(data ?? []).length === 0 ? (
          <p className="text-sm text-slate-500 dark:text-slate-400">No shared mailboxes yet.</p>
        ) : (
          <ul className="space-y-2">
            {(data ?? []).map((row: any) => (
              <li key={row.id} className="text-sm text-slate-700 dark:text-slate-200">{row.display_name}</li>
            ))}
          </ul>
        )}
      </div>
    </main>
  );
}