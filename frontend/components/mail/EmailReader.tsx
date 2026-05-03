"use client";

import { MailItem } from "@/types";
import { formatDate } from "@/lib/utils";

interface EmailReaderProps {
  item?: MailItem | null;
  folder?: string;
  uid?: string;
}

export function EmailReader({ item, folder, uid }: EmailReaderProps) {
  if (!item) {
    return (
      <div className="rounded-xl border border-dashed border-slate-300 p-8 text-center text-sm text-slate-500 dark:border-slate-700">
        {folder && uid
          ? `Loading message ${uid} from ${folder}...`
          : "Select an email"}
      </div>
    );
  }
  return (
    <article className="rounded-xl border border-slate-200 p-4 dark:border-slate-800">
      <h2 className="text-lg font-semibold">{item.subject}</h2>
      <p className="mb-2 text-sm text-slate-500">
        From: {item.from_email || item.from}
      </p>
      <p className="mb-4 text-xs text-slate-400">{formatDate(item.date)}</p>
      <div className="whitespace-pre-wrap text-sm">
        {item.body || item.snippet}
      </div>
    </article>
  );
}
