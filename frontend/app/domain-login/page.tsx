"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { Eye, EyeOff, Globe, Loader2, Mail } from "lucide-react";
import Link from "next/link";
import { api } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";

export default function DomainAdminLoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loginMutation = useMutation({
    mutationFn: () => api.login({ email, password }),
    onSuccess: (data) => {
      setError(null);
      try {
        const payload = JSON.parse(atob(data.access_token.split(".")[1]));
        if (payload.role !== "domain_admin" && payload.role !== "super_admin") {
          setError("Access denied. Domain admin credentials required.");
          return;
        }
        login(data.access_token, data.refresh_token);
        router.push("/domain-admin");
      } catch {
        setError("Invalid token received.");
      }
    },
    onError: (err: unknown) => {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail ?? "Invalid credentials.";
      setError(detail);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError("Email and password are required.");
      return;
    }
    setError(null);
    loginMutation.mutate();
  };

  return (
    <div className="relative flex min-h-screen w-full overflow-hidden bg-white dark:bg-slate-950">
      {/* Gradient blobs */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -right-32 -top-32 h-[500px] w-[500px] rounded-full bg-gradient-to-br from-violet-500/15 to-indigo-500/15 blur-[80px]" />
        <div className="absolute -bottom-32 -left-32 h-[500px] w-[500px] rounded-full bg-gradient-to-tr from-blue-500/15 to-cyan-500/15 blur-[80px]" />
      </div>

      {/* Login panel */}
      <div className="relative flex w-full flex-col items-center justify-center px-6 lg:w-1/2">
        <div className="w-full max-w-sm">
          {/* Logo */}
          <div className="mb-10 flex flex-col items-center">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-600 to-indigo-600 shadow-lg shadow-violet-500/30">
              <Globe className="h-7 w-7 text-white" />
            </div>
            <h1 className="mt-4 text-2xl font-bold text-gray-900 dark:text-white">
              Domain Admin
            </h1>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Manage your domain and mailboxes
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email */}
            <div className="space-y-1.5">
              <label
                htmlFor="domain-email"
                className="text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                <input
                  id="domain-email"
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@yourdomain.com"
                  className="w-full rounded-xl border border-gray-200 bg-gray-50 py-3 pl-10 pr-4 text-sm text-gray-900 placeholder-gray-400 outline-none transition focus:border-violet-500 focus:bg-white focus:ring-2 focus:ring-violet-500/20 dark:border-slate-700 dark:bg-slate-800/50 dark:text-white dark:placeholder-slate-500 dark:focus:border-violet-400 dark:focus:bg-slate-800"
                />
              </div>
            </div>

            {/* Password */}
            <div className="space-y-1.5">
              <label
                htmlFor="domain-password"
                className="text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                Password
              </label>
              <div className="relative">
                <input
                  id="domain-password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 pr-12 text-sm text-gray-900 placeholder-gray-400 outline-none transition focus:border-violet-500 focus:bg-white focus:ring-2 focus:ring-violet-500/20 dark:border-slate-700 dark:bg-slate-800/50 dark:text-white dark:placeholder-slate-500 dark:focus:border-violet-400 dark:focus:bg-slate-800"
                />
                <button
                  type="button"
                  tabIndex={-1}
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:text-slate-500 dark:hover:text-slate-300 transition"
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
              <div className="flex justify-end">
                <Link
                  href="/forgot-password"
                  className="text-xs text-violet-600 hover:text-violet-700 dark:text-violet-400 dark:hover:text-violet-300"
                >
                  Forgot password?
                </Link>
              </div>
            </div>

            {/* Error */}
            {error && (
              <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600 dark:border-red-800/50 dark:bg-red-900/20 dark:text-red-400">
                {error}
              </div>
            )}

            {/* Submit */}
            <button
              id="domain-login-submit"
              type="submit"
              disabled={loginMutation.isPending}
              className="mt-2 flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-violet-500/25 transition hover:from-violet-500 hover:to-indigo-500 disabled:opacity-60"
            >
              {loginMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                "Sign In"
              )}
            </button>
          </form>

          <div className="mt-6 flex items-center justify-between text-xs text-gray-400 dark:text-gray-600">
            <Link href="/login" className="hover:text-gray-600 dark:hover:text-gray-400 transition">
              ← User Login
            </Link>
            <Link href="/admin-login" className="hover:text-gray-600 dark:hover:text-gray-400 transition">
              Super Admin →
            </Link>
          </div>
        </div>
      </div>

      {/* Right info panel (desktop) */}
      <div className="relative hidden flex-1 items-center justify-center bg-gradient-to-br from-violet-600 to-indigo-700 lg:flex">
        <div className="p-12 text-white">
          <h2 className="text-3xl font-bold leading-tight">
            Manage your domain,
            <br />
            your way.
          </h2>
          <p className="mt-4 max-w-xs text-violet-200">
            Full control over mailboxes, users, DNS, backups, and compliance — all in one place.
          </p>

          <div className="mt-10 space-y-4">
            {[
              { emoji: "📬", text: "Create & manage mailboxes" },
              { emoji: "👥", text: "Invite and manage users" },
              { emoji: "🔒", text: "DNS verification & DKIM" },
              { emoji: "💾", text: "One-click domain backups" },
              { emoji: "📊", text: "eDiscovery & audit logs" },
            ].map((item) => (
              <div key={item.text} className="flex items-center gap-3">
                <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-white/15 text-lg">
                  {item.emoji}
                </span>
                <span className="text-sm text-violet-100">{item.text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
