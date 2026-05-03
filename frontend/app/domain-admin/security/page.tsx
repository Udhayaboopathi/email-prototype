"use client";

import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getDomainApiKeys,
  createDomainApiKey,
  getDomainAuditLogs,
} from "@/lib/api";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { MoreHorizontal, PlusCircle } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { toast } from "sonner";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";

const apiKeySchema = z.object({
  name: z.string().min(1, "API key name is required"),
});

type ApiKeyFormValues = z.infer<typeof apiKeySchema>;

function ApiKeysTab() {
  const queryClient = useQueryClient();
  const [isCreateKeyOpen, setCreateKeyOpen] = useState(false);
  const [newApiKey, setNewApiKey] = useState<string | null>(null);

  const { data, isLoading, error } = useQuery({
    queryKey: ["domainApiKeys"],
    queryFn: getDomainApiKeys,
  });

  const form = useForm<ApiKeyFormValues>({
    resolver: zodResolver(apiKeySchema),
    defaultValues: { name: "" },
  });

  const createApiKeyMutation = useMutation({
    mutationFn: createDomainApiKey,
    onSuccess: (data) => {
      toast.success("API Key created successfully!");
      setNewApiKey(data.key);
      setCreateKeyOpen(false);
      form.reset();
      queryClient.invalidateQueries({ queryKey: ["domainApiKeys"] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to create API key.");
    },
  });

  const onSubmit = (data: ApiKeyFormValues) => {
    createApiKeyMutation.mutate(data);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle>API Keys</CardTitle>
          <Dialog open={isCreateKeyOpen} onOpenChange={setCreateKeyOpen}>
            <DialogTrigger asChild>
              <Button size="sm">
                <PlusCircle className="mr-2 h-4 w-4" />
                Create API Key
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New API Key</DialogTitle>
                <DialogDescription>
                  This key will have permissions to access your domain's
                  resources.
                </DialogDescription>
              </DialogHeader>
              <Form {...form}>
                <form
                  onSubmit={form.handleSubmit(onSubmit)}
                  className="space-y-4 py-4"
                >
                  <FormField
                    control={form.control}
                    name="name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Key Name</FormLabel>
                        <FormControl>
                          <Input {...field} placeholder="e.g., My App" />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <DialogFooter>
                    <Button
                      variant="outline"
                      onClick={() => setCreateKeyOpen(false)}
                    >
                      Cancel
                    </Button>
                    <Button
                      type="submit"
                      disabled={createApiKeyMutation.isPending}
                    >
                      {createApiKeyMutation.isPending
                        ? "Creating..."
                        : "Create Key"}
                    </Button>
                  </DialogFooter>
                </form>
              </Form>
            </DialogContent>
          </Dialog>
        </div>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Created At</TableHead>
              <TableHead>Last Used</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && (
              <TableRow>
                <TableCell colSpan={3}>Loading API keys...</TableCell>
              </TableRow>
            )}
            {error && (
              <TableRow>
                <TableCell colSpan={3}>Error loading API keys.</TableCell>
              </TableRow>
            )}
            {data?.map((key: any) => (
              <TableRow key={key.id}>
                <TableCell>{key.name}</TableCell>
                <TableCell>
                  {new Date(key.created_at).toLocaleString()}
                </TableCell>
                <TableCell>
                  {key.last_used_at
                    ? new Date(key.last_used_at).toLocaleString()
                    : "Never"}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        {newApiKey && (
          <Dialog defaultOpen>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>API Key Created</DialogTitle>
                <DialogDescription>
                  Please copy your new API key. You won't be able to see it
                  again.
                </DialogDescription>
              </DialogHeader>
              <div className="mt-4 bg-slate-100 dark:bg-slate-800 p-4 rounded-md">
                <code className="break-all">{newApiKey}</code>
              </div>
              <DialogFooter>
                <Button onClick={() => setNewApiKey(null)}>Close</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        )}
      </CardContent>
    </Card>
  );
}

function AuditLogsTab() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["domainAuditLogs"],
    queryFn: getDomainAuditLogs,
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Audit Logs</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Timestamp</TableHead>
              <TableHead>User</TableHead>
              <TableHead>Action</TableHead>
              <TableHead>Details</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && (
              <TableRow>
                <TableCell colSpan={4}>Loading audit logs...</TableCell>
              </TableRow>
            )}
            {error && (
              <TableRow>
                <TableCell colSpan={4}>Error loading audit logs.</TableCell>
              </TableRow>
            )}
            {data?.map((log: any) => (
              <TableRow key={log.id}>
                <TableCell>
                  {new Date(log.created_at).toLocaleString()}
                </TableCell>
                <TableCell>{log.user?.email || "System"}</TableCell>
                <TableCell>
                  <Badge>{log.action}</Badge>
                </TableCell>
                <TableCell className="font-mono text-xs">
                  {log.details}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}

export default function SecurityPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Security</h1>
      <Tabs defaultValue="api-keys">
        <TabsList>
          <TabsTrigger value="api-keys">API Keys</TabsTrigger>
          <TabsTrigger value="audit-logs">Audit Logs</TabsTrigger>
        </TabsList>
        <TabsContent value="api-keys">
          <ApiKeysTab />
        </TabsContent>
        <TabsContent value="audit-logs">
          <AuditLogsTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}
