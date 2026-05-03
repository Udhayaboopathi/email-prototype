"use client";

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Users, Mailbox, HardDrive, AlertTriangle, ShieldCheck } from 'lucide-react';
import { getDomainAdminDashboard } from '@/lib/api';
import { Progress } from '@/components/ui/progress';

const StatCard = ({ title, value, icon: Icon, description }: { title: string, value: string | number, icon: React.ElementType, description: string }) => (
    <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{title}</CardTitle>
            <Icon className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
            <div className="text-2xl font-bold">{value}</div>
            <p className="text-xs text-muted-foreground">{description}</p>
        </CardContent>
    </Card>
);

export default function DomainAdminDashboard() {
    const { data, isLoading, error } = useQuery({
        queryKey: ['domainAdminDashboard'],
        queryFn: getDomainAdminDashboard,
    });

    if (isLoading) return <div>Loading dashboard...</div>;
    if (error) return <div>Error loading dashboard data.</div>;

    const { stats, email_traffic, dns_records } = data || {};
    const storagePercentage = stats ? (stats.storage_used_gb / stats.storage_limit_gb) * 100 : 0;

    return (
        <div className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                <StatCard title="Total Users" value={stats?.total_users} icon={Users} description="Users in your domain" />
                <StatCard title="Total Mailboxes" value={stats?.total_mailboxes} icon={Mailbox} description="Mailboxes in your domain" />
                <StatCard title="Aliases" value={stats?.total_aliases} icon={Users} description="Alias pointing to mailboxes" />
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Storage Usage</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-2">
                        <Progress value={storagePercentage} />
                        <div className="flex justify-between text-sm">
                            <span>{stats?.storage_used_gb.toFixed(2)} GB used</span>
                            <span>{stats?.storage_limit_gb} GB total</span>
                        </div>
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>Email Traffic (Last 30 Days)</CardTitle>
                </CardHeader>
                <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={email_traffic}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="date" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Line type="monotone" dataKey="received" stroke="#3b82f6" name="Received" />
                            <Line type="monotone" dataKey="sent" stroke="#84cc16" name="Sent" />
                        </LineChart>
                    </ResponsiveContainer>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>DNS Configuration</CardTitle>
                    <CardDescription>Required DNS records for your domain to function correctly.</CardDescription>
                </CardHeader>
                <CardContent>
                    <ul className="space-y-2">
                        {dns_records?.map((record: any) => (
                            <li key={record.name} className="flex items-center justify-between p-2 rounded-md bg-gray-50 dark:bg-gray-800/50">
                                <div className="font-mono text-sm">
                                    <span className="font-bold">{record.type}</span> {record.name} {'->'} <span className="text-muted-foreground">{record.value}</span>
                                </div>
                                {record.is_valid ? (
                                    <div className="flex items-center text-green-600">
                                        <ShieldCheck className="h-4 w-4 mr-1" /> Valid
                                    </div>
                                ) : (
                                    <div className="flex items-center text-red-600">
                                        <AlertTriangle className="h-4 w-4 mr-1" /> Invalid
                                    </div>
                                )}
                            </li>
                        ))}
                    </ul>
                </CardContent>
            </Card>
        </div>
    );
}

