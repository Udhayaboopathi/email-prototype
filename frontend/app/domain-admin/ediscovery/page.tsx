"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

export default function DomainAdminEdiscoveryPage() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState("");

  const runExport = async () => {
    const token = getAccessToken();
    if (!token) return;
    const exportRow = await api.createEdiscoveryExport(token, { query });
    setResult(`Export ${exportRow.id} queued.`);
  };

  return (
    <main className="space-y-4 p-4 md:p-6">
      <h1 className="text-xl font-semibold text-slate-900 dark:text-slate-100">eDiscovery</h1>
      <div className="space-y-2 rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
        <textarea value={query} onChange={(e) => setQuery(e.target.value)} rows={4} className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" placeholder="from:person@example.com subject:invoice" />
        <button onClick={runExport} className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white dark:bg-slate-100 dark:text-slate-900">Create Export</button>
        {result ? <p className="text-sm text-slate-600 dark:text-slate-300">{result}</p> : null}
      </div>
    </main>
  );
}