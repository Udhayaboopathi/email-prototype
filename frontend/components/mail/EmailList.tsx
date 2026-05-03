"use client";

import { useState } from "react";
import { useMail } from "@/hooks/useMail";
import { MailItem } from "@/types";
import { EmailListItem } from "@/components/mail/EmailListItem";

interface EmailListProps {
  folder: string;
  onSelect?: (item: MailItem) => void;
}

export function EmailList({ folder, onSelect }: EmailListProps) {
  const { messages, loading, error } = useMail(folder);

  if (loading) {
    return (
      <div className="p-6 text-center text-sm text-slate-500">Loading...</div>
    );
  }

  if (error) {
    return (
      <div className="p-6 text-center text-sm text-red-500">{error}</div>
    );
  }

  const handleSelect = (item: MailItem) => {
    onSelect?.(item);
  };

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 dark:border-slate-800">
      {messages.length === 0 ? (
        <div className="p-6 text-center text-sm text-slate-500">
          No messages
        </div>
      ) : (
        messages.map((item) => (
          <EmailListItem key={item.uid || item.id} item={item} onSelect={handleSelect} />
        ))
      )}
    </div>
  );
}
