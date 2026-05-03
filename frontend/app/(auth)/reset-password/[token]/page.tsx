"use client";

import { useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { KeyRound, Eye, EyeOff } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";

const PasswordStrengthIndicator = ({ score }: { score: number }) => {
  const levels = [
    { color: "bg-red-500", text: "Weak" },
    { color: "bg-orange-500", text: "Fair" },
    { color: "bg-yellow-500", text: "Good" },
    { color: "bg-green-500", text: "Strong" },
  ];

  return (
    <div className="flex items-center space-x-2">
      <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${levels[score]?.color || "bg-gray-200"}`}
          style={{ width: `${(score + 1) * 25}%` }}
        />
      </div>
      <span className="text-sm text-gray-600 dark:text-gray-400 w-14 text-right">
        {levels[score]?.text}
      </span>
    </div>
  );
};

export default function ResetPasswordPage() {
  const router = useRouter();
  const params = useParams();
  const { toast } = useToast();
  const token = params.token as string;

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [strength, setStrength] = useState(0);

  const mutation = useMutation({
    mutationFn: api.confirmPasswordReset,
    onSuccess: () => {
      toast({
        title: "Success",
        description: "Your password has been updated. Please sign in.",
        variant: "success",
      });
      router.push("/login");
    },
    onError: (err: any) => {
      setError(
        err.response?.data?.detail ||
          "Invalid or expired token. Please try again.",
      );
    },
  });

  const checkStrength = (pw: string) => {
    let score = 0;
    if (pw.length > 8) score++;
    if (pw.match(/[a-z]/) && pw.match(/[A-Z]/)) score++;
    if (pw.match(/[0-9]/)) score++;
    if (pw.match(/[^a-zA-Z0-9]/)) score++;
    if (pw.length === 0) score = -1;
    setStrength(score > 3 ? 3 : score);
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newPassword = e.target.value;
    setPassword(newPassword);
    checkStrength(newPassword);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    if (strength < 2) {
      setError("Password is not strong enough.");
      return;
    }
    mutation.mutate({ token, new_password: password });
  };

  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-gray-100 dark:bg-gray-900 bg-gradient-to-br from-gray-50 to-gray-200 dark:from-gray-800 dark:to-gray-950">
      <div className="w-full max-w-md rounded-lg border-t-4 border-blue-600 bg-white p-8 shadow-lg dark:bg-gray-800 dark:border-blue-500">
        <div className="mb-6 flex flex-col items-center text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gray-200 dark:bg-gray-700">
            <KeyRound className="h-8 w-8 text-gray-600 dark:text-gray-400" />
          </div>
          <h1 className="mt-4 text-2xl font-bold text-gray-900 dark:text-white">
            Set New Password
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Choose a strong password to protect your account.
          </p>
        </div>

        {error && (
          <div className="mb-4 rounded-md bg-red-100 p-3 text-center text-sm text-red-700 dark:bg-red-900/20 dark:text-red-400">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative">
            <label htmlFor="password" className="sr-only">
              New Password
            </label>
            <Input
              id="password"
              type={showPassword ? "text" : "password"}
              placeholder="New Password"
              value={password}
              onChange={handlePasswordChange}
              required
              autoFocus
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-500"
            >
              {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
            </button>
          </div>

          {password && <PasswordStrengthIndicator score={strength} />}

          <div>
            <label htmlFor="confirm-password" className="sr-only">
              Confirm New Password
            </label>
            <Input
              id="confirm-password"
              type="password"
              placeholder="Confirm New Password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          </div>

          <Button
            type="submit"
            className="w-full"
            disabled={mutation.isPending}
          >
            {mutation.isPending ? "Setting Password..." : "Set New Password"}
          </Button>
        </form>
      </div>
    </div>
  );
}
