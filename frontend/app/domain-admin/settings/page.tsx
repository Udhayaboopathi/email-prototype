"use client";

import React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getDomainSettings, updateDomainSettings } from "@/lib/api";
import { Button } from "@/components/ui/button";
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
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";

const settingsSchema = z.object({
  catch_all_address: z.string().email().optional().or(z.literal("")),
  // Add other domain settings here
});

type SettingsFormValues = z.infer<typeof settingsSchema>;

export default function SettingsPage() {
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ["domainSettings"],
    queryFn: getDomainSettings,
  });

  const form = useForm<SettingsFormValues>({
    resolver: zodResolver(settingsSchema),
    values: {
      catch_all_address: data?.catch_all_address || "",
    },
  });

  const updateSettingsMutation = useMutation({
    mutationFn: updateDomainSettings,
    onSuccess: () => {
      toast.success("Settings updated successfully!");
      queryClient.invalidateQueries({ queryKey: ["domainSettings"] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to update settings.");
    },
  });

  const onSubmit = (data: SettingsFormValues) => {
    updateSettingsMutation.mutate(data);
  };

  if (isLoading) return <div>Loading settings...</div>;
  if (error) return <div>Error loading settings.</div>;

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Domain Settings</h1>
      <Card>
        <CardHeader>
          <CardTitle>General Settings</CardTitle>
          <CardDescription>Manage your domain's configuration.</CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="catch_all_address"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Catch-all Address</FormLabel>
                    <FormControl>
                      <Input
                        {...field}
                        placeholder="e.g., catchall@example.com"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Example of another setting */}
              {/* <FormField
                                control={form.control}
                                name="some_other_setting"
                                render={({ field }) => (
                                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                                        <div className="space-y-0.5">
                                            <FormLabel className="text-base">
                                                Enable Feature X
                                            </FormLabel>
                                            <CardDescription>
                                                A brief description of what this feature does.
                                            </CardDescription>
                                        </div>
                                        <FormControl>
                                            <Switch
                                                checked={field.value}
                                                onCheckedChange={field.onChange}
                                            />
                                        </FormControl>
                                    </FormItem>
                                )}
                            /> */}

              <Button type="submit" disabled={updateSettingsMutation.isPending}>
                {updateSettingsMutation.isPending
                  ? "Saving..."
                  : "Save Changes"}
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}
