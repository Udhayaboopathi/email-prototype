"use client";

import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { getAuditLogs } from "@/lib/api";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { DateRangePicker } from "@/components/ui/date-range-picker";
import { DateRange } from "react-day-picker";

export default function AuditLogsPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [actionFilter, setActionFilter] = useState("all");
  const [dateRange, setDateRange] = useState<DateRange | undefined>(undefined);

  const { data, isLoading, error } = useQuery({
    queryKey: [
      "auditLogs",
      {
        search: searchTerm,
        action: actionFilter,
        from: dateRange?.from,
        to: dateRange?.to,
      },
    ],
    queryFn: () =>
      getAuditLogs({
        search: searchTerm,
        action: actionFilter,
        from: dateRange?.from,
        to: dateRange?.to,
      }),
    placeholderData: (prev: unknown) => prev,
  });

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Audit Logs</h1>
      </div>
      <div className="flex items-center space-x-2">
        <Input
          placeholder="Search by user, IP, or details..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-72"
        />
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline">
              Action:{" "}
              {actionFilter.charAt(0).toUpperCase() + actionFilter.slice(1)}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuItem onSelect={() => setActionFilter("all")}>
              All
            </DropdownMenuItem>
            <DropdownMenuItem onSelect={() => setActionFilter("login")}>
              Login
            </DropdownMenuItem>
            <DropdownMenuItem onSelect={() => setActionFilter("logout")}>
              Logout
            </DropdownMenuItem>
            <DropdownMenuItem onSelect={() => setActionFilter("domain_add")}>
              Domain Add
            </DropdownMenuItem>
            <DropdownMenuItem onSelect={() => setActionFilter("user_create")}>
              User Create
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
        <DateRangePicker onUpdate={({ range }) => setDateRange(range)} />
      </div>

      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Timestamp</TableHead>
              <TableHead>User</TableHead>
              <TableHead>Action</TableHead>
              <TableHead>Details</TableHead>
              <TableHead>IP Address</TableHead>
              <TableHead>Country</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && (
              <TableRow>
                <TableCell colSpan={6}>Loading audit logs...</TableCell>
              </TableRow>
            )}
            {error && (
              <TableRow>
                <TableCell colSpan={6}>Error loading audit logs.</TableCell>
              </TableRow>
            )}
            {data?.map((log: any) => (
              <TableRow key={log.id}>
                <TableCell>
                  {new Date(log.timestamp).toLocaleString()}
                </TableCell>
                <TableCell>{log.user_email}</TableCell>
                <TableCell>{log.action}</TableCell>
                <TableCell className="max-w-xs truncate">
                  {log.details}
                </TableCell>
                <TableCell>{log.ip_address}</TableCell>
                <TableCell>{log.country}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
