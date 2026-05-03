"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useAppStore } from "@/store";
import {
  LayoutDashboard,
  Globe,
  Database,
  ShieldCheck,
  Settings,
  Users,
  Mail,
  Shield,
  FileText,
  Inbox,
  Send,
  Archive,
  Trash2,
  Star,
  AlertOctagon,
} from "lucide-react";
import { UserRole } from "@/types";

interface SidebarProps {
  role?: UserRole;
}

const superAdminNav = [
  { name: "Dashboard", href: "/super-admin", icon: LayoutDashboard },
  { name: "Domains", href: "/super-admin/domains", icon: Globe },
  { name: "Backups", href: "/super-admin/backups", icon: Database },
  { name: "Audit Logs", href: "/super-admin/audit-logs", icon: ShieldCheck },
  { name: "Settings", href: "/super-admin/settings", icon: Settings },
];

const domainAdminNav = [
  { name: "Dashboard", href: "/domain-admin", icon: LayoutDashboard },
  { name: "Users", href: "/domain-admin/users", icon: Users },
  { name: "Mailboxes", href: "/domain-admin/mailboxes", icon: Mail },
  { name: "Security", href: "/domain-admin/security", icon: Shield },
  { name: "Settings", href: "/domain-admin/settings", icon: Settings },
];

const userMailNav = [
  { name: "Inbox", href: "/mail/inbox", icon: Inbox },
  { name: "Starred", href: "/mail/starred", icon: Star },
  { name: "Sent", href: "/mail/sent", icon: Send },
  { name: "Drafts", href: "/mail/drafts", icon: FileText },
  { name: "Spam", href: "/mail/spam", icon: AlertOctagon },
  { name: "Archive", href: "/mail/archive", icon: Archive },
  { name: "Trash", href: "/mail/trash", icon: Trash2 },
];

export function Sidebar({ role }: SidebarProps) {
  const pathname = usePathname();
  const { isSidebarCollapsed } = useAppStore();

  const navItems =
    role === "super_admin"
      ? superAdminNav
      : role === "domain_admin"
        ? domainAdminNav
        : userMailNav;

  return (
    <aside
      className={cn(
        "h-screen bg-background border-r transition-all duration-300 ease-in-out",
        isSidebarCollapsed ? "w-20" : "w-64",
      )}
    >
      <div className="flex h-16 items-center justify-center border-b">
        <FileText className="h-8 w-8" />
        {!isSidebarCollapsed && (
          <span className="ml-2 font-bold">Email Platform</span>
        )}
      </div>
      <nav className="mt-4">
        <ul>
          {navItems.map((item) => (
            <li key={item.name} className="px-4 py-2">
              <Link href={item.href} passHref>
                <Button
                  variant={pathname === item.href ? "secondary" : "ghost"}
                  className="w-full justify-start"
                >
                  <item.icon
                    className={cn("h-5 w-5", !isSidebarCollapsed && "mr-3")}
                  />
                  {!isSidebarCollapsed && <span>{item.name}</span>}
                </Button>
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
}
