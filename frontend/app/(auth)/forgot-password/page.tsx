"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { Mail } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";

export default function ForgotPasswordPage() {
  const { toast } = useToast();
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const mutation = useMutation({
    mutationFn: api.requestPasswordReset,
    onSuccess: () => {
      setSubmitted(true);
    },
    onError: (error: any) => {
      // Still show success message to prevent email enumeration
      setSubmitted(true);
      console.error("Forgot password error:", error);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    mutation.mutate({ email });
  };

  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-gray-100 dark:bg-gray-900 bg-gradient-to-br from-gray-50 to-gray-200 dark:from-gray-800 dark:to-gray-950">
      <div className="w-full max-w-md rounded-lg border-t-4 border-blue-600 bg-white p-8 shadow-lg dark:bg-gray-800 dark:border-blue-500">
        <div className="mb-6 flex flex-col items-center text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gray-200 dark:bg-gray-700">
            <Mail className="h-8 w-8 text-gray-600 dark:text-gray-400" />
          </div>
          <h1 className="mt-4 text-2xl font-bold text-gray-900 dark:text-white">
            Forgot Password
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            {submitted
              ? "Check your inbox for a reset link."
              : "Enter your email to reset your password."}
          </p>
        </div>

        {submitted ? (
          <div className="text-center">
            <p className="text-gray-800 dark:text-gray-200">
              If an account with that email exists, a password reset link has
              been sent.
            </p>
            <Button asChild className="mt-6 w-full">
              <Link href="/login">Back to Sign In</Link>
            </Button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="email" className="sr-only">
                Email
              </label>
              <Input
                id="email"
                type="email"
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoFocus
              />
            </div>
            <Button
              type="submit"
              className="w-full"
              disabled={mutation.isPending}
            >
              {mutation.isPending ? "Sending..." : "Send Reset Link"}
            </Button>
            <div className="text-center">
              <Button variant="link" asChild>
                <Link href="/login">Back to Sign In</Link>
              </Button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
