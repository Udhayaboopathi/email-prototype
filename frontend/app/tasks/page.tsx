"use client";


export const dynamic = 'force-dynamic';
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

export default function TasksPage() {
  const token = getAccessToken();
  const { data } = useQuery({ queryKey: ["tasks"], queryFn: async () => (token ? api.listTasks(token) : []), enabled: Boolean(token) });

  return (
    <main className="space-y-4 p-4 md:p-6">
      <h1 className="text-xl font-semibold text-slate-900 dark:text-slate-100">Tasks</h1>
      <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
        {(data ?? []).length === 0 ? <p className="text-sm text-slate-500 dark:text-slate-400">No tasks yet.</p> : null}
        <ul className="space-y-2">
          {(data ?? []).map((task: any) => (
            <li key={task.id} className="rounded-lg border border-slate-200 p-3 text-sm dark:border-slate-700">
              <p className="font-medium text-slate-900 dark:text-slate-100">{task.title}</p>
              <p className="text-slate-600 dark:text-slate-300">{task.description}</p>
            </li>
          ))}
        </ul>
      </div>
    </main>
  );
}