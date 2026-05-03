"use client";


export const dynamic = 'force-dynamic';
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

export default function NotesPage() {
  const token = getAccessToken();
  const { data } = useQuery({ queryKey: ["notes"], queryFn: async () => (token ? api.listNotes(token) : []), enabled: Boolean(token) });

  return (
    <main className="space-y-4 p-4 md:p-6">
      <h1 className="text-xl font-semibold text-slate-900 dark:text-slate-100">Notes</h1>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {(data ?? []).map((note: any) => (
          <article key={note.id} className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
            <h2 className="font-medium text-slate-900 dark:text-slate-100">{note.title}</h2>
            <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{note.body}</p>
          </article>
        ))}
      </div>
    </main>
  );
}