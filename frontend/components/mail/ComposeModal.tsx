"use client";

import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/Modal";
import { api } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

interface ComposeModalProps {
  open: boolean;
  onClose: () => void;
}

export function ComposeModal({ open, onClose }: ComposeModalProps) {
  const [to, setTo] = useState("");
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [sending, setSending] = useState(false);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    const token = getAccessToken();
    if (!token) return;
    setSending(true);
    try {
      await api.sendMail(token, {
        from_email: "noreply@example.com",
        to: to.split(",").map(v => v.trim()).filter(Boolean),
        subject,
        body_html: body,
        body_text: body
      });
      onClose();
      setTo("");
      setSubject("");
      setBody("");
    } finally {
      setSending(false);
    }
  };

  return (
    <Modal open={open} title="Compose" onClose={onClose}>
      <form onSubmit={submit} className="space-y-3">
        <Input placeholder="To" value={to} onChange={e => setTo(e.target.value)} />
        <Input placeholder="Subject" value={subject} onChange={e => setSubject(e.target.value)} />
        <textarea
          value={body}
          onChange={e => setBody(e.target.value)}
          className="h-40 w-full rounded-lg border border-slate-300 bg-white p-3 text-sm dark:border-slate-700 dark:bg-slate-900"
        />
        <Button type="submit" disabled={sending}>
          {sending ? "Sending..." : "Send"}
        </Button>
      </form>
    </Modal>
  );
}
