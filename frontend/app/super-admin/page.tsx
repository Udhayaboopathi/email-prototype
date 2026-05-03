"use client";

import React from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Globe, Mail, HardDrive, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import { getSuperAdminStats, getSuperAdminAuditLogs } from "@/lib/api";

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ElementType;
  description?: string;
  colorClass?: string;
}

const StatCard = ({ title, value, icon: Icon, description, colorClass = "text-blue-500" }: StatCardProps) => (
  <Card className="dark:bg-gray-800 dark:border-gray-700">
    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</CardTitle>
      <Icon className={`h-5 w-5 ${colorClass}`} />
    </CardHeader>
    <CardContent>
      <div className="text-2xl font-bold text-gray-900 dark:text-white">{value}</div>
      {description && (
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{description}</p>
      )}
    </CardContent>
  </Card>
);

export default function SuperAdminDashboard() {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ["superAdminStats"],
    queryFn: getSuperAdminStats,
  });

  const { data: auditLogs } = useQuery({
    queryKey: ["superAdminAuditLogs"],
    queryFn: getSuperAdminAuditLogs,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center gap-2 text-red-500 p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
        <AlertCircle className="h-5 w-5" />
        <span>Failed to load dashboard data. Check backend connectivity.</span>
      </div>
    );
  }

  const storagePercent =
    stats?.storage_total_gb > 0
      ? Math.round((stats.storage_used_gb / stats.storage_total_gb) * 100)
      : 0;

  const storageBarColor =
    storagePercent >= 90
      ? "bg-red-500"
      : storagePercent >= 70
      ? "bg-amber-500"
      : "bg-green-500";

  return (
    <div className="space-y-6">
      {/* Stats row */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Domains"
          value={stats?.total_domains ?? 0}
          icon={Globe}
          description="All hosted domains"
          colorClass="text-blue-500"
        />
        <StatCard
          title="Total Mailboxes"
          value={stats?.total_mailboxes ?? 0}
          icon={Mail}
          description="Across all domains"
          colorClass="text-indigo-500"
        />
        <StatCard
          title="Platform Storage"
          value={`${stats?.storage_used_gb ?? 0} / ${stats?.storage_total_gb ?? 0} GB`}
          icon={HardDrive}
          description={`${storagePercent}% used`}
          colorClass="text-green-500"
        />
        <StatCard
          title="DNS Verified"
          value={`${stats?.dns_verified ?? 0} / ${stats?.total_domains ?? 0}`}
          icon={CheckCircle}
          description="Domains with valid DNS"
          colorClass="text-emerald-500"
        />
      </div>

      {/* Storage bar */}
      <Card className="dark:bg-gray-800 dark:border-gray-700">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
            Platform Storage Usage
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
            <div
              className={`h-3 rounded-full transition-all duration-500 ${storageBarColor}`}
              style={{ width: `${Math.min(storagePercent, 100)}%` }}
            />
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            {stats?.storage_used_gb ?? 0} GB used of {stats?.storage_total_gb ?? 0} GB
          </p>
        </CardContent>
      </Card>

      {/* Recent Audit Logs */}
      <Card className="dark:bg-gray-800 dark:border-gray-700">
        <CardHeader>
          <CardTitle className="text-base font-semibold text-gray-900 dark:text-white">
            Recent Audit Log
          </CardTitle>
        </CardHeader>
        <CardContent>
          {!auditLogs || auditLogs.length === 0 ? (
            <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-8">
              No audit log entries yet.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-500 dark:text-gray-400 border-b dark:border-gray-700">
                    <th className="pb-2 pr-4 font-medium">Action</th>
                    <th className="pb-2 pr-4 font-medium">Target</th>
                    <th className="pb-2 pr-4 font-medium">IP</th>
                    <th className="pb-2 font-medium">Time</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                  {(auditLogs as Array<{
                    id: string;
                    action: string;
                    target?: string;
                    ip_address?: string;
                    created_at: string;
                  }>).slice(0, 10).map((log) => (
                    <tr key={log.id} className="text-gray-700 dark:text-gray-300">
                      <td className="py-2 pr-4 font-mono text-xs">{log.action}</td>
                      <td className="py-2 pr-4 text-gray-500 dark:text-gray-400 truncate max-w-[180px]">
                        {log.target ?? "—"}
                      </td>
                      <td className="py-2 pr-4 text-gray-500 dark:text-gray-400">
                        {log.ip_address ?? "—"}
                      </td>
                      <td className="py-2 text-gray-400 dark:text-gray-500 whitespace-nowrap">
                        {new Date(log.created_at).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
