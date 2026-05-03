"use client";

import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getDomainMailboxes, createDomainMailbox } from "@/lib/api";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
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
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";

const mailboxSchema = z.object({
  email: z.string().email(),
  user_id: z.string().uuid(),
});

type MailboxFormValues = z.infer<typeof mailboxSchema>;

export default function MailboxesPage() {
  const queryClient = useQueryClient();
  const [isCreateMailboxOpen, setCreateMailboxOpen] = useState(false);

  const { data, isLoading, error } = useQuery({
    queryKey: ["domainMailboxes"],
    queryFn: getDomainMailboxes,
  });

  const form = useForm<MailboxFormValues>({
    resolver: zodResolver(mailboxSchema),
    defaultValues: {
      email: "",
      user_id: "",
    },
  });

  const createMailboxMutation = useMutation({
    mutationFn: createDomainMailbox,
    onSuccess: () => {
      toast.success("Mailbox created successfully!");
      setCreateMailboxOpen(false);
      form.reset();
      queryClient.invalidateQueries({ queryKey: ["domainMailboxes"] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to create mailbox.");
    },
  });

  const onSubmit = (data: MailboxFormValues) => {
    createMailboxMutation.mutate(data);
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Mailboxes</h1>
        <Dialog open={isCreateMailboxOpen} onOpenChange={setCreateMailboxOpen}>
          <DialogTrigger asChild>
            <Button>
              <PlusCircle className="mr-2 h-4 w-4" />
              Create Mailbox
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Mailbox</DialogTitle>
              <DialogDescription>
                Create a new mailbox and assign it to a user.
              </DialogDescription>
            </DialogHeader>
            <Form {...form}>
              <form
                onSubmit={form.handleSubmit(onSubmit)}
                className="space-y-4 py-4"
              >
                <FormField
                  control={form.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Email Address</FormLabel>
                      <FormControl>
                        <Input {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="user_id"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>User ID</FormLabel>
                      <FormControl>
                        <Input {...field} placeholder="Assign to user by ID" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <DialogFooter>
                  <Button
                    variant="outline"
                    onClick={() => setCreateMailboxOpen(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    disabled={createMailboxMutation.isPending}
                  >
                    {createMailboxMutation.isPending
                      ? "Creating..."
                      : "Create Mailbox"}
                  </Button>
                </DialogFooter>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Email</TableHead>
              <TableHead>Assigned User</TableHead>
              <TableHead>Storage Usage</TableHead>
              <TableHead>
                <span className="sr-only">Actions</span>
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && (
              <TableRow>
                <TableCell colSpan={4}>Loading mailboxes...</TableCell>
              </TableRow>
            )}
            {error && (
              <TableRow>
                <TableCell colSpan={4}>Error loading mailboxes.</TableCell>
              </TableRow>
            )}
            {data?.map((mailbox: any) => (
              <TableRow key={mailbox.id}>
                <TableCell className="font-medium">{mailbox.email}</TableCell>
                <TableCell>{mailbox.user.email}</TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <Progress
                      value={
                        (mailbox.storage_used_gb / mailbox.storage_limit_gb) *
                        100
                      }
                      className="w-32"
                    />
                    <span className="text-xs text-muted-foreground">
                      {mailbox.storage_used_gb.toFixed(2)} /{" "}
                      {mailbox.storage_limit_gb} GB
                    </span>
                  </div>
                </TableCell>
                <TableCell>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" className="h-8 w-8 p-0">
                        <span className="sr-only">Open menu</span>
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem>Edit</DropdownMenuItem>
                      <DropdownMenuItem>Manage Aliases</DropdownMenuItem>
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
