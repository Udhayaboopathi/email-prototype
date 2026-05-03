"use client";

import { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Eye, EyeOff, Mail } from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Whitelabel } from "@/types";
import { useAppStore } from "@/store";

type LoginStep = "credentials" | "totp";

function LoginPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login, setTempToken, clearTempToken, tempToken } = useAuth();
  const { toast } = useToast();
  const setLoading = useAppStore((state) => state.setLoading);

  const [step, setStep] = useState<LoginStep>("credentials");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [totpCode, setTotpCode] = useState<string[]>(Array(6).fill(""));
  const [isBackupCode, setIsBackupCode] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const domain = searchParams.get("domain");

  const { data: whitelabel, isLoading: isLoadingWhitelabel } =
    useQuery<Whitelabel>({
      queryKey: ["whitelabel", domain],
      queryFn: () => api.getWhitelabelSettings(domain!),
      enabled: !!domain,
    });

  useEffect(() => {
    if (whitelabel?.primary_color) {
      document.documentElement.style.setProperty(
        "--brand-primary",
        whitelabel.primary_color,
      );
    }
    return () => {
      document.documentElement.style.removeProperty("--brand-primary");
    };
  }, [whitelabel]);

  const loginMutation = useMutation({
    mutationFn: api.login,
    onSuccess: (data) => {
      setError(null);
      if (data.requires_totp) {
        setTempToken(data.temp_token);
        setStep("totp");
      } else {
        login(data.access_token, data.refresh_token, rememberMe);
        try {
          const payload = JSON.parse(atob(data.access_token.split(".")[1]));
          redirectUser(payload.role);
        } catch {
          router.push("/mail/inbox");
        }
      }
    },
    onError: (err: any) => {
      const errorMessage =
        err.response?.data?.detail || "Incorrect email or password pls try agin";
      if (errorMessage.includes("inactive")) {
        setError("Your account has been deactivated.");
      } else if (errorMessage.includes("suspended")) {
        setError("This domain has been suspended.");
      } else {
        setError("Incorrect email or password.");
      }
    },
  });

  const totpMutation = useMutation({
    mutationFn: api.verifyTotp,
    onSuccess: (data) => {
      setError(null);
      login(data.access_token, data.refresh_token, rememberMe);
      try {
        const payload = JSON.parse(atob(data.access_token.split(".")[1]));
        redirectUser(payload.role);
      } catch {
        router.push("/mail/inbox");
      }
    },
    onError: () => {
      setError("Invalid code, please try again.");
      setTotpCode(Array(6).fill(""));
    },
  });

  const redirectUser = (role: string | undefined) => {
    switch (role) {
      case "super_admin":
        router.push("/super-admin");
        break;
      case "domain_admin":
        router.push("/domain-admin");
        break;
      case "user":
        router.push("/mail/inbox");
        break;
      default:
        router.push("/login");
    }
  };

  const handleLoginSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    loginMutation.mutate({ email, password });
  };

  const handleTotpChange = (index: number, value: string) => {
    if (!/^\d?$/.test(value)) return;

    const newCode = [...totpCode];
    newCode[index] = value;
    setTotpCode(newCode);

    if (value && index < 5) {
      document.getElementById(`totp-${index + 1}`)?.focus();
    }

    if (newCode.every((digit) => digit !== "") && !isBackupCode) {
      handleTotpSubmit(newCode.join(""));
    }
  };

  const handleTotpKeyDown = (
    index: number,
    e: React.KeyboardEvent<HTMLInputElement>,
  ) => {
    if (e.key === "Backspace" && !totpCode[index] && index > 0) {
      document.getElementById(`totp-${index - 1}`)?.focus();
    }
  };

  const handleTotpSubmit = (code: string) => {
    if (!tempToken) {
      setError("Session expired. Please try again.");
      setStep("credentials");
      return;
    }
    setError(null);
    totpMutation.mutate({
      temp_token: tempToken,
      code,
      is_backup_code: isBackupCode,
    });
  };

  const handleTotpFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleTotpSubmit(totpCode.join(""));
  };

  const handleBackToCredentials = () => {
    setStep("credentials");
    clearTempToken();
    setError(null);
    setPassword("");
    setTotpCode(Array(6).fill(""));
  };

  useEffect(() => {
    setLoading(
      loginMutation.isPending || totpMutation.isPending || isLoadingWhitelabel,
    );
  }, [
    loginMutation.isPending,
    totpMutation.isPending,
    isLoadingWhitelabel,
    setLoading,
  ]);

  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-gray-100 dark:bg-gray-900 bg-gradient-to-br from-gray-50 to-gray-200 dark:from-gray-800 dark:to-gray-950">
      <div
        className="w-full max-w-md rounded-lg border-t-4 bg-white p-8 shadow-lg dark:bg-gray-800"
        style={{
          borderColor:
            whitelabel?.primary_color || "var(--brand-primary, #3b82f6)",
        }}
      >
        <div className="mb-6 flex flex-col items-center text-center">
          {whitelabel?.logo_url ? (
            <img
              src={whitelabel.logo_url}
              alt={whitelabel.company_name ?? "Company logo"}
              className="h-16 w-auto"
            />
          ) : (
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gray-200 dark:bg-gray-700">
              <Mail className="h-8 w-8 text-gray-600 dark:text-gray-400" />
            </div>
          )}
          <h1 className="mt-4 text-2xl font-bold text-gray-900 dark:text-white">
            {whitelabel?.company_name || "MailOS"}
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            {step === "credentials"
              ? "Sign in to your account"
              : "Two-Factor Authentication"}
          </p>
        </div>

        {error && (
          <div className="mb-4 rounded-md bg-red-100 p-3 text-center text-sm text-red-700 dark:bg-red-900/20 dark:text-red-400">
            {error}
          </div>
        )}

        {step === "credentials" ? (
          <form onSubmit={handleLoginSubmit} className="space-y-4">
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
                autoComplete="email"
              />
            </div>
            <div className="relative">
              <label htmlFor="password" className="sr-only">
                Password
              </label>
              <Input
                id="password"
                type={showPassword ? "text" : "password"}
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-500"
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Checkbox
                  id="remember-me"
                  checked={rememberMe}
                  onCheckedChange={(checked) => setRememberMe(!!checked)}
                />
                <label
                  htmlFor="remember-me"
                  className="ml-2 block text-sm text-gray-900 dark:text-gray-300"
                >
                  Remember me
                </label>
              </div>
              <div className="text-sm">
                <Link
                  href="/forgot-password"
                  className="font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300"
                >
                  Forgot password?
                </Link>
              </div>
            </div>
            <Button
              type="submit"
              className="w-full"
              disabled={loginMutation.isPending}
              style={{
                backgroundColor:
                  whitelabel?.primary_color || "var(--brand-primary, #3b82f6)",
              }}
            >
              {loginMutation.isPending ? "Signing in..." : "Sign in"}
            </Button>
          </form>
        ) : (
          <form onSubmit={handleTotpFormSubmit} className="space-y-6">
            <p className="text-center text-gray-600 dark:text-gray-400">
              Enter the 6-digit code from your authenticator app.
            </p>

            {isBackupCode ? (
              <Input
                id="backup-code"
                type="text"
                placeholder="Enter backup code"
                value={totpCode.join("")}
                onChange={(e) => setTotpCode(e.target.value.split(""))}
                required
                autoFocus
              />
            ) : (
              <div className="flex justify-center space-x-2">
                {totpCode.map((digit, index) => (
                  <Input
                    key={index}
                    id={`totp-${index}`}
                    type="text"
                    maxLength={1}
                    value={digit}
                    onChange={(e) => handleTotpChange(index, e.target.value)}
                    onKeyDown={(e) => handleTotpKeyDown(index, e)}
                    className="h-12 w-10 text-center text-lg font-semibold"
                    required
                  />
                ))}
              </div>
            )}

            <div className="text-center text-sm">
              <button
                type="button"
                onClick={() => setIsBackupCode(!isBackupCode)}
                className="font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300"
              >
                {isBackupCode
                  ? "Use authenticator app instead"
                  : "Use a backup code"}
              </button>
            </div>

            <div className="flex items-center space-x-4">
              <Button
                variant="outline"
                onClick={handleBackToCredentials}
                className="w-full"
              >
                Back
              </Button>
              <Button
                type="submit"
                className="w-full"
                disabled={totpMutation.isPending}
                style={{
                  backgroundColor:
                    whitelabel?.primary_color ||
                    "var(--brand-primary, #3b82f6)",
                }}
              >
                {totpMutation.isPending ? "Verifying..." : "Verify"}
              </Button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <LoginPageContent />
    </Suspense>
  );
}
