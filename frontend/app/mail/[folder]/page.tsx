"use client";

import { useParams } from "next/navigation";
import { EmailList } from "@/components/mail/EmailList";

export default function FolderPage() {
  const params = useParams<{ folder: string }>();
  return (
    <section className="space-y-4">
      <h1 className="text-xl font-semibold capitalize text-slate-900 dark:text-slate-100">{params.folder}</h1>
      <EmailList folder={params.folder} />
    </section>
  );
}