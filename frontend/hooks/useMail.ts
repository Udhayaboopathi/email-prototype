"use client";

import { useCallback, useEffect, useState } from "react";

import { api } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { MailItem } from "@/types";

export function useMail(folder: string) {
  const [messages, setMessages] = useState<MailItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) {
      setError("Not authenticated");
      setLoading(false);
      return;
    }
    try {
      setLoading(true);
      const rows = await api.listMail(token, folder);
      setMessages(rows);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch mail");
    } finally {
      setLoading(false);
    }
  }, [folder]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return { messages, loading, error, refresh };
}
