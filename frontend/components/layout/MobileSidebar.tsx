"use client";

import Link from "next/link";

interface MobileSidebarProps {
  open: boolean;
  onClose: () => void;
}

export function MobileSidebar({ open, onClose }: MobileSidebarProps) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-40 bg-black/40 md:hidden" onClick={onClose}>
      <div className="h-full w-64 bg-white p-4 dark:bg-slate-950" onClick={event => event.stopPropagation()}>
        <div className="mb-4 text-lg font-semibold">Menu</div>
        <nav className="space-y-2">
          {["/mail/INBOX", "/calendar", "/tasks", "/settings"].map(path => (
            <Link key={path} href={path} onClick={onClose} className="block rounded-lg px-3 py-2 hover:bg-slate-100 dark:hover:bg-slate-800">
              {path.replace("/", "")}
            </Link>
          ))}
        </nav>
      </div>
    </div>
  );
}
