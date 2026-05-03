"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  Globe,
  HardDrive,
  ScrollText,
  Settings,
  Bell,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Mail,
} from "lucide-react";
import { useAuth } from "@/lib/auth";
import { useAppStore } from "@/store";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const navItems = [
  { href: "/super-admin", icon: LayoutDashboard, label: "Dashboard" },
  { href: "/super-admin/domains", icon: Globe, label: "Domains" },
  { href: "/super-admin/backups", icon: HardDrive, label: "Backups" },
  { href: "/super-admin/audit-logs", icon: ScrollText, label: "Audit Logs" },
  { href: "/super-admin/settings", icon: Settings, label: "Settings" },
];

function Sidebar({
  isCollapsed,
  toggleCollapse,
}: {
  isCollapsed: boolean;
  toggleCollapse: () => void;
}) {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <aside
      className={`flex flex-col bg-gray-50 dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 transition-all duration-300 ${isCollapsed ? "w-20" : "w-60"}`}
    >
      <div
        className={`flex items-center h-16 px-4 border-b border-gray-200 dark:border-gray-800 ${isCollapsed ? "justify-center" : "justify-between"}`}
      >
        {!isCollapsed && (
          <Link href="/super-admin" className="flex items-center gap-2">
            <Mail className="h-6 w-6 text-blue-600" />
            <span className="font-bold text-lg">MailOS</span>
          </Link>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleCollapse}
          className="hidden lg:flex"
        >
          {isCollapsed ? <ChevronRight /> : <ChevronLeft />}
        </Button>
      </div>
      <nav className="flex-1 px-2 py-4 space-y-1">
        <TooltipProvider delayDuration={0}>
          {navItems.map((item) => (
            <Tooltip key={item.href}>
              <TooltipTrigger asChild>
                <Link
                  href={item.href}
                  className={`flex items-center p-2 rounded-md text-sm font-medium transition-colors ${
                    pathname === item.href
                      ? "bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300"
                      : "text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
                  } ${isCollapsed ? "justify-center" : ""}`}
                >
                  <item.icon
                    className={`h-5 w-5 ${!isCollapsed ? "mr-3" : ""}`}
                  />
                  {!isCollapsed && item.label}
                </Link>
              </TooltipTrigger>
              {isCollapsed && (
                <TooltipContent side="right">{item.label}</TooltipContent>
              )}
            </Tooltip>
          ))}
        </TooltipProvider>
      </nav>
      <div className="px-2 py-4 mt-auto border-t border-gray-200 dark:border-gray-800">
        <div
          className={`flex items-center ${isCollapsed ? "justify-center" : "justify-between"} p-2`}
        >
          {!isCollapsed && (
            <div className="flex items-center gap-2 truncate">
              <Avatar className="h-8 w-8">
                <AvatarImage src={user?.avatar_url} />
                <AvatarFallback>
                  {user?.email?.[0].toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <span className="text-sm font-medium truncate">
                {user?.email}
              </span>
            </div>
          )}
          <TooltipProvider delayDuration={0}>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" onClick={logout}>
                  <LogOut className="h-5 w-5" />
                </Button>
              </TooltipTrigger>
              {isCollapsed && (
                <TooltipContent side="right">Sign Out</TooltipContent>
              )}
            </Tooltip>
          </TooltipProvider>
        </div>
      </div>
    </aside>
  );
}

function Topbar({ pageTitle }: { pageTitle: string }) {
  const { toggleDarkMode, isDarkMode } = useAppStore();
  return (
    <header className="flex items-center h-16 px-6 bg-white dark:bg-gray-900/50 border-b border-gray-200 dark:border-gray-800">
      <h1 className="text-xl font-semibold">{pageTitle}</h1>
      <div className="ml-auto flex items-center space-x-4">
        <Button variant="ghost" size="icon">
          <Bell className="h-5 w-5" />
          <span className="sr-only">Notifications</span>
        </Button>
        <Button variant="ghost" size="icon" onClick={toggleDarkMode}>
          {isDarkMode ? (
            <Settings className="h-5 w-5" />
          ) : (
            <Settings className="h-5 w-5" />
          )}
        </Button>
      </div>
    </header>
  );
}

export default function SuperAdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { user, isLoading } = useAuth();
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
  const pathname = usePathname();

  const pageTitle =
    navItems.find((item) => item.href === pathname)?.label || "Dashboard";

  if (isLoading) {
    return <div>Loading session...</div>;
  }

  if (!user || user.role !== "super_admin") {
    router.replace("/login");
    return null;
  }

  return (
    <div className="flex h-screen bg-gray-100 dark:bg-gray-950 text-gray-900 dark:text-gray-100">
      <Sidebar
        isCollapsed={isSidebarCollapsed}
        toggleCollapse={() => setSidebarCollapsed(!isSidebarCollapsed)}
      />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Topbar pageTitle={pageTitle} />
        <main className="flex-1 overflow-x-hidden overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
