"use client";

interface ToastProps {
  message: string;
  type?: "success" | "error";
}

export function Toast({ message, type = "success" }: ToastProps) {
  const style = type === "success" ? "bg-green-600" : "bg-red-600";
  return <div className={`rounded-lg px-3 py-2 text-sm text-white ${style}`}>{message}</div>;
}
