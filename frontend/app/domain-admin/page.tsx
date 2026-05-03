"use client";

import React from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Mailbox,
  HardDrive,
  CheckCircle,
  XCircle,
  Users,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { getDomainAdminStats, getDomainDnsRecords } from "@/lib/api";

const StatCard = ({
  title,
  value,
  icon: Icon,
  description,
  colorClass = "text-blue-500",
}: {
  title: string;
  value: string | number;
  icon: React.ElementType;
  description?: string;
  colorClass?: string;
}) => (
  <Card className="dark:bg-gray-800 dark:border-gray-700">
    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
        {title}
      </CardTitle>
      <Icon className={`h-5 w-5 ${colorClass}`} />
    </CardHeader>
    <CardContent>
      <div className="text-2xl font-bold text-gray-900 dark:text-white">
        {value}
      </div>
      {description && (
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
          {description}
        </p>
      )}
    </CardContent>
  </Card>
);

export default function DomainAdminDashboard() {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ["domainAdminStats"],
    queryFn: getDomainAdminStats,
  });

  const { data: dnsRecords } = useQuery({
    queryKey: ["domainDnsRecords"],
    queryFn: getDomainDnsRecords,
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
    stats?.storage_quota_gb > 0
      ? Math.round((stats.storage_used_gb / stats.storage_quota_gb) * 100)
      : 0;

  const storageBarColor =
    storagePercent >= 90
      ? "bg-red-500"
      : storagePercent >= 70
      ? "bg-amber-500"
      : "bg-green-500";

  return (
    <div className="space-y-6">
      {/* Domain header */}
      {stats?.domain_name && (
        <div className="flex items-center gap-3 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
          <div>
            <p className="text-sm text-blue-600 dark:text-blue-400 font-medium">
              Managing domain
            </p>
            <p className="text-lg font-bold text-blue-800 dark:text-blue-200">
              {stats.domain_name}
            </p>
          </div>
          {stats.dns_verified ? (
            <span className="ml-auto flex items-center gap-1 text-green-600 dark:text-green-400 text-sm font-medium">
              <CheckCircle className="h-4 w-4" /> DNS Verified
            </span>
          ) : (
            <span className="ml-auto flex items-center gap-1 text-amber-600 dark:text-amber-400 text-sm font-medium">
              <XCircle className="h-4 w-4" /> DNS Pending
            </span>
          )}
        </div>
      )}

      {/* Stat cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard
          title="Total Mailboxes"
          value={stats?.total_mailboxes ?? 0}
          icon={Mailbox}
          description="All mailboxes in your domain"
          colorClass="text-blue-500"
        />
        <StatCard
          title="Active Mailboxes"
          value={stats?.active_mailboxes ?? 0}
          icon={Users}
          description="Currently active accounts"
          colorClass="text-green-500"
        />
        <StatCard
          title="Storage Used"
          value={`${stats?.storage_used_gb ?? 0} / ${stats?.storage_quota_gb ?? 0} GB`}
          icon={HardDrive}
          description={`${storagePercent}% utilised`}
          colorClass="text-indigo-500"
        />
      </div>

      {/* Storage bar */}
      <Card className="dark:bg-gray-800 dark:border-gray-700">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
            Storage Usage
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
            {stats?.storage_used_gb ?? 0} GB used of {stats?.storage_quota_gb ?? 0} GB
          </p>
        </CardContent>
      </Card>

      {/* DNS Records */}
      <Card className="dark:bg-gray-800 dark:border-gray-700">
        <CardHeader>
          <CardTitle className="text-base font-semibold text-gray-900 dark:text-white">
            Required DNS Records
          </CardTitle>
        </CardHeader>
        <CardContent>
          {!dnsRecords || dnsRecords.length === 0 ? (
            <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-8">
              No DNS records found.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-500 dark:text-gray-400 border-b dark:border-gray-700">
                    <th className="pb-2 pr-4 font-medium">Type</th>
                    <th className="pb-2 pr-4 font-medium">Name</th>
                    <th className="pb-2 pr-4 font-medium">Value</th>
                    <th className="pb-2 font-medium">Purpose</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                  {(dnsRecords as Array<{
                    type: string;
                    name: string;
                    value: string;
                    purpose?: string;
                  }>).map((record, i) => (
                    <tr key={i} className="text-gray-700 dark:text-gray-300">
                      <td className="py-2 pr-4">
                        <span className="font-mono text-xs bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded font-bold">
                          {record.type}
                        </span>
                      </td>
                      <td className="py-2 pr-4 font-mono text-xs truncate max-w-[160px]">
                        {record.name}
                      </td>
                      <td className="py-2 pr-4 font-mono text-xs text-gray-500 dark:text-gray-400 truncate max-w-[200px]">
                        {record.value}
                      </td>
                      <td className="py-2 text-gray-400 dark:text-gray-500 text-xs">
                        {record.purpose ?? "—"}
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
