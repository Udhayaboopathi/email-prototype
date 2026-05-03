"use client";

import { Button } from "@/components/ui/button";
import { useUIStore } from "@/store";

export function Topbar() {
  const darkMode = useUIStore(state => state.darkMode);
  const toggleDarkMode = useUIStore(state => state.toggleDarkMode);
  return (
    <header className="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-3 dark:border-slate-800 dark:bg-slate-950">
      <div className="text-sm text-slate-500">Self Hosted Mail Platform</div>
      <Button variant="secondary" onClick={toggleDarkMode}>
        {darkMode ? "Light" : "Dark"}
      </Button>
    </header>
  );
}
