"use client";

import React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getBackupJobs, triggerBackup } from "@/lib/api";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MoreHorizontal, PlayCircle } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { toast } from "sonner";
import { Card } from "@/components/ui/card";

export default function BackupsPage() {
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ["backupJobs"],
    queryFn: getBackupJobs,
  });

  const triggerBackupMutation = useMutation({
    mutationFn: triggerBackup,
    onSuccess: () => {
      toast.success("Backup job started successfully!");
      queryClient.invalidateQueries({ queryKey: ["backupJobs"] });
    },
    onError: (error: any) => {
      toast.error(
        error.response?.data?.detail || "Failed to start backup job.",
      );
    },
  });

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Backup Jobs</h1>
        <Button
          onClick={() => triggerBackupMutation.mutate()}
          disabled={triggerBackupMutation.isPending}
        >
          <PlayCircle className="mr-2 h-4 w-4" />
          {triggerBackupMutation.isPending
            ? "Starting..."
            : "Trigger New Backup"}
        </Button>
      </div>

      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Job ID</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Started At</TableHead>
              <TableHead>Finished At</TableHead>
              <TableHead>Size</TableHead>
              <TableHead>Location</TableHead>
              <TableHead>
                <span className="sr-only">Actions</span>
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && (
              <TableRow>
                <TableCell colSpan={7}>Loading backup jobs...</TableCell>
              </TableRow>
            )}
            {error && (
              <TableRow>
                <TableCell colSpan={7}>Error loading backup jobs.</TableCell>
              </TableRow>
            )}
            {data?.map((job: any) => (
              <TableRow key={job.id}>
                <TableCell className="font-mono">{job.id}</TableCell>
                <TableCell>
                  <Badge
                    variant={
                      job.status === "completed"
                        ? "success"
                        : job.status === "failed"
                          ? "destructive"
                          : job.status === "in_progress"
                            ? "default"
                            : "secondary"
                    }
                  >
                    {job.status}
                  </Badge>
                </TableCell>
                <TableCell>
                  {new Date(job.started_at).toLocaleString()}
                </TableCell>
                <TableCell>
                  {job.finished_at
                    ? new Date(job.finished_at).toLocaleString()
                    : "N/A"}
                </TableCell>
                <TableCell>
                  {job.size_gb ? `${job.size_gb.toFixed(2)} GB` : "N/A"}
                </TableCell>
                <TableCell>{job.location}</TableCell>
                <TableCell>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" className="h-8 w-8 p-0">
                        <span className="sr-only">Open menu</span>
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem>Download</DropdownMenuItem>
                      <DropdownMenuItem>View Logs</DropdownMenuItem>
                      <DropdownMenuItem className="text-red-600">
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
