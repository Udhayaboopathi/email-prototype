"use client";

import { FormEvent, useState } from "react";
import { api } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

export default function DomainAdminRetentionPage() {
  const [days, setDays] = useState<number>(90);
  const [saved, setSaved] = useState(false);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    const token = getAccessToken();
    if (!token) return;
    await api.updateRetention(token, { retention_days: days });
    setSaved(true);
  };

  return (
    <main className="space-y-4 p-4 md:p-6">
      <h1 className="text-xl font-semibold text-slate-900 dark:text-slate-100">Retention Policy</h1>
      <form onSubmit={submit} className="space-y-3 rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
        <label className="text-sm text-slate-600 dark:text-slate-300">Retention Days</label>
        <input type="number" min={0} value={days} onChange={(e) => setDays(Number(e.target.value))} className="w-32 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" />
        <button type="submit" className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white dark:bg-slate-100 dark:text-slate-900">Update</button>
        {saved ? <p className="text-sm text-emerald-600 dark:text-emerald-400">Retention updated.</p> : null}
      </form>
    </main>
  );
}