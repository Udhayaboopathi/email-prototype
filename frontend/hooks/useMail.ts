"use client";

import { useCallback, useEffect, useState } from "react";
import { listMail } from "@/lib/api";
import { MailItem } from "@/types";

export function useMail(folder: string) {
  const [messages, setMessages] = useState<MailItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      // Token is injected automatically by the axios interceptor in api.ts
      const rows = await listMail(folder);
      setMessages(Array.isArray(rows) ? rows : []);
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : (err as { response?: { data?: { detail?: string } } })?.response?.data
              ?.detail ?? "Failed to fetch mail";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [folder]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return { messages, loading, error, refresh };
}
