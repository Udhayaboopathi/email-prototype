"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { MailX, Loader2, ShieldCheck, ShieldAlert } from "lucide-react";

import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import Link from "next/link";

type UnsubscribeStatus = "loading" | "success" | "error" | "idle";

export default function UnsubscribePage() {
  const params = useParams();
  const router = useRouter();
  const token = params.token as string;

  const [status, setStatus] = useState<UnsubscribeStatus>("idle");
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: api.unsubscribe,
    onSuccess: () => {
      setStatus("success");
    },
    onError: (err: any) => {
      setError(
        err.response?.data?.detail || "Invalid or expired unsubscribe link.",
      );
      setStatus("error");
    },
  });

  const handleUnsubscribe = () => {
    setStatus("loading");
    mutation.mutate(token);
  };

  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-gray-100 dark:bg-gray-900 bg-gradient-to-br from-gray-50 to-gray-200 dark:from-gray-800 dark:to-gray-950">
      <div className="w-full max-w-md rounded-lg border-t-4 border-blue-600 bg-white p-8 text-center shadow-lg dark:bg-gray-800 dark:border-blue-500">
        <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-gray-200 dark:bg-gray-700">
          {status === "loading" && (
            <Loader2 className="h-8 w-8 animate-spin text-gray-600 dark:text-gray-400" />
          )}
          {status === "success" && (
            <ShieldCheck className="h-8 w-8 text-green-600 dark:text-green-400" />
          )}
          {status === "error" && (
            <ShieldAlert className="h-8 w-8 text-red-600 dark:text-red-400" />
          )}
          {status === "idle" && (
            <MailX className="h-8 w-8 text-gray-600 dark:text-gray-400" />
          )}
        </div>

        <h1 className="mt-4 text-2xl font-bold text-gray-900 dark:text-white">
          Unsubscribe
        </h1>

        <div className="mt-4 min-h-[80px]">
          {status === "idle" && (
            <>
              <p className="text-gray-600 dark:text-gray-400">
                Are you sure you want to unsubscribe from future mailings?
              </p>
              <Button onClick={handleUnsubscribe} className="mt-6 w-full">
                Confirm Unsubscribe
              </Button>
            </>
          )}
          {status === "loading" && (
            <p className="text-gray-600 dark:text-gray-400">
              Unsubscribing you now...
            </p>
          )}
          {status === "success" && (
            <div>
              <p className="text-green-700 dark:text-green-300">
                You have been successfully unsubscribed.
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                You will no longer receive these emails.
              </p>
            </div>
          )}
          {status === "error" && (
            <div>
              <p className="text-red-700 dark:text-red-300">
                {error || "An error occurred."}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                This link may be expired or invalid.
              </p>
            </div>
          )}
        </div>

        <div className="mt-8">
          <Button variant="link" asChild>
            <Link href="/">Go to Homepage</Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
