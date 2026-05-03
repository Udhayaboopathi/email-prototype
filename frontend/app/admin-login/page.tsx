"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { Eye, EyeOff, Shield, Loader2 } from "lucide-react";
import Link from "next/link";
import { api } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import { getRoleFromToken } from "@/lib/jwt";

export default function SuperAdminLoginPage() {
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
      const role = getRoleFromToken(data.access_token ?? "");
      if (role !== "super_admin") {
        setError("Access denied. Super admin credentials required.");
        return;
      }
      login(data.access_token, data.refresh_token);
      router.push("/super-admin");
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
    <div className="relative flex min-h-screen w-full overflow-hidden bg-[#0a0f1e]">
      {/* Animated gradient background */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -left-40 -top-40 h-96 w-96 rounded-full bg-blue-700/20 blur-[100px]" />
        <div className="absolute -bottom-40 -right-40 h-96 w-96 rounded-full bg-indigo-700/20 blur-[100px]" />
        <div className="absolute left-1/2 top-1/2 h-64 w-64 -translate-x-1/2 -translate-y-1/2 rounded-full bg-blue-900/20 blur-[120px]" />
        {/* Grid lines */}
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage:
              "linear-gradient(to right, #4f6ef7 1px, transparent 1px), linear-gradient(to bottom, #4f6ef7 1px, transparent 1px)",
            backgroundSize: "48px 48px",
          }}
        />
      </div>

      {/* Left branding panel */}
      <div className="relative hidden flex-1 flex-col items-center justify-center lg:flex">
        <div className="flex flex-col items-center gap-6 text-center">
          <div className="flex h-24 w-24 items-center justify-center rounded-2xl bg-blue-600/20 ring-1 ring-blue-500/30">
            <Shield className="h-12 w-12 text-blue-400" />
          </div>
          <div>
            <h1 className="text-4xl font-bold tracking-tight text-white">
              MailOS
            </h1>
            <p className="mt-2 text-lg text-blue-300/70">Super Admin Portal</p>
          </div>
          <div className="mt-8 grid grid-cols-2 gap-4 text-sm">
            {[
              { label: "Domain Management", icon: "🌐" },
              { label: "Platform Backups", icon: "💾" },
              { label: "Audit Logs", icon: "📋" },
              { label: "System Settings", icon: "⚙️" },
            ].map((f) => (
              <div
                key={f.label}
                className="flex items-center gap-2 rounded-lg bg-white/5 px-4 py-3 ring-1 ring-white/10"
              >
                <span>{f.icon}</span>
                <span className="text-white/70">{f.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right login panel */}
      <div className="relative flex w-full items-center justify-center px-6 lg:w-[480px] lg:border-l lg:border-white/10">
        <div className="w-full max-w-sm">
          {/* Mobile logo */}
          <div className="mb-8 flex items-center gap-3 lg:hidden">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600/20 ring-1 ring-blue-500/30">
              <Shield className="h-5 w-5 text-blue-400" />
            </div>
            <span className="text-xl font-bold text-white">MailOS Admin</span>
          </div>

          <div className="mb-8">
            <h2 className="text-2xl font-bold text-white">Welcome back</h2>
            <p className="mt-1 text-sm text-white/50">
              Sign in to the super admin console
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium uppercase tracking-wider text-white/50">
                Email Address
              </label>
              <input
                id="admin-email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@yourdomain.com"
                className="w-full rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-sm text-white placeholder-white/20 outline-none transition focus:border-blue-500/60 focus:bg-white/8 focus:ring-1 focus:ring-blue-500/30"
              />
            </div>

            {/* Password */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium uppercase tracking-wider text-white/50">
                Password
              </label>
              <div className="relative">
                <input
                  id="admin-password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full rounded-lg border border-white/10 bg-white/5 px-4 py-3 pr-12 text-sm text-white placeholder-white/20 outline-none transition focus:border-blue-500/60 focus:bg-white/8 focus:ring-1 focus:ring-blue-500/30"
                />
                <button
                  type="button"
                  tabIndex={-1}
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-white/30 hover:text-white/60 transition"
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>

            {/* Error */}
            {error && (
              <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
                {error}
              </div>
            )}

            {/* Submit */}
            <button
              id="admin-login-submit"
              type="submit"
              disabled={loginMutation.isPending}
              className="mt-2 flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-600/20 transition hover:bg-blue-500 disabled:opacity-60"
            >
              {loginMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Authenticating...
                </>
              ) : (
                "Sign In to Admin Console"
              )}
            </button>
          </form>

          <div className="mt-6 flex items-center justify-between text-xs text-white/30">
            <Link href="/login" className="hover:text-white/60 transition">
              ← User Login
            </Link>
            <Link href="/domain-login" className="hover:text-white/60 transition">
              Domain Admin →
            </Link>
          </div>

          <p className="mt-8 text-center text-xs text-white/20">
            Unauthorized access is prohibited and monitored.
          </p>
        </div>
      </div>
    </div>
  );
}
