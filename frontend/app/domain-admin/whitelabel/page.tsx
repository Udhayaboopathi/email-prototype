"use client";

import { FormEvent, useState } from "react";
import { api } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

export default function DomainAdminWhitelabelPage() {
  const [companyName, setCompanyName] = useState("");
  const [primaryColor, setPrimaryColor] = useState("#0f172a");
  const [saved, setSaved] = useState(false);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    const token = getAccessToken();
    if (!token) return;
    await api.updateWhitelabel(token, { whitelabel_company_name: companyName, whitelabel_primary_color: primaryColor });
    setSaved(true);
  };

  return (
    <main className="space-y-4 p-4 md:p-6">
      <h1 className="text-xl font-semibold text-slate-900 dark:text-slate-100">Whitelabel</h1>
      <form onSubmit={submit} className="space-y-3 rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
        <input value={companyName} onChange={(e) => setCompanyName(e.target.value)} placeholder="Company name" className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" />
        <input value={primaryColor} onChange={(e) => setPrimaryColor(e.target.value)} type="color" className="h-10 w-20 rounded border border-slate-300 dark:border-slate-700" />
        <button type="submit" className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white dark:bg-slate-100 dark:text-slate-900">Save</button>
        {saved ? <p className="text-sm text-emerald-600 dark:text-emerald-400">Saved.</p> : null}
      </form>
    </main>
  );
}