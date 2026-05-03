"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

export default function DomainAdminBackupPage() {
  const [status, setStatus] = useState("");
  const triggerBackup = async () => {
    const token = getAccessToken();
    if (!token) return;
    await api.domainBackup(token);
    setStatus("Domain backup queued.");
  };

  return (
    <main className="space-y-4 p-4 md:p-6">
      <h1 className="text-xl font-semibold text-slate-900 dark:text-slate-100">Domain Backup</h1>
      <button onClick={triggerBackup} className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white dark:bg-slate-100 dark:text-slate-900">
        Create Backup
      </button>
      {status ? <p className="text-sm text-emerald-600 dark:text-emerald-400">{status}</p> : null}
    </main>
  );
}