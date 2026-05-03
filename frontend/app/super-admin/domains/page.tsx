"use client";

import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getSuperAdminDomains, inviteDomainAdmin, createDomain, regenerateDkim } from "@/lib/api";
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
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  MoreHorizontal,
  PlusCircle,
  Globe,
  Eye,
  EyeOff,
  CheckCircle2,
  Info,
  Copy,
  KeyRound,
  RefreshCw,
} from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { Card } from "@/components/ui/card";

// ── Types ─────────────────────────────────────────────────────────────────────
interface DomainForm {
  name: string;
  admin_email: string;
  admin_password: string;
  storage_quota_mb: string; // string for input, convert to number on submit
  dns_mode: "auto" | "manual";
  cloudflare_token: string;
}

interface DnsRecord {
  type: string;
  name: string;
  value: string;
}

interface CreateDomainResult {
  domain: {
    id: string;
    name: string;
    is_verified: boolean;
    is_suspended: boolean;
    storage_quota_mb: number | null;
    cloudflare_zone_id: string | null;
  };
  admin_email: string;
  dns_mode: "auto" | "manual";
  dns_records: DnsRecord[] | null;
  cloudflare_error: string | null;
}

interface DkimResult {
  domain: string;
  selector: string;
  dns_record: { type: string; name: string; value: string };
  cloudflare: string | null;
}

const EMPTY_FORM: DomainForm = {
  name: "",
  admin_email: "",
  admin_password: "",
  storage_quota_mb: "",
  dns_mode: "manual",
  cloudflare_token: "",
};

// ── Component ─────────────────────────────────────────────────────────────────
export default function DomainsPage() {
  const queryClient = useQueryClient();

  // ── search / filter state
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  // ── Add Domain dialog state
  const [isAddDomainOpen, setAddDomainOpen] = useState(false);
  const [form, setForm] = useState<DomainForm>(EMPTY_FORM);
  const [showPassword, setShowPassword] = useState(false);
  const [step, setStep] = useState<"form" | "dns">("form");
  const [dnsResult, setDnsResult] = useState<CreateDomainResult | null>(null);

  // ── Invite Domain Admin dialog state
  const [isInviteDialogOpen, setInviteDialogOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteDomainId, setInviteDomainId] = useState("");

  // ── DKIM regeneration dialog state
  const [dkimDialogOpen, setDkimDialogOpen] = useState(false);
  const [dkimResult, setDkimResult] = useState<DkimResult | null>(null);
  const [dkimLoading, setDkimLoading] = useState<string | null>(null); // domainId being processed

  // ── Data fetching
  const { data, isLoading, error } = useQuery({
    queryKey: ["domains", { search: searchTerm, status: statusFilter }],
    queryFn: () => getSuperAdminDomains({ search: searchTerm, status: statusFilter }),
    placeholderData: (prev: unknown) => prev,
  });

  // ── Mutations
  const addDomainMutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => createDomain(payload),
    onSuccess: (data: CreateDomainResult) => {
      queryClient.invalidateQueries({ queryKey: ["domains"] });
      setDnsResult(data);
      if (data.cloudflare_error) {
        toast.warning(`Domain created but Cloudflare DNS setup failed: ${data.cloudflare_error}`);
      } else if (data.dns_mode === "auto") {
        toast.success("Domain created and DNS auto-configured via Cloudflare!");
      } else {
        toast.success("Domain created! Configure DNS records manually.");
      }
      setStep("dns");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to create domain.");
    },
  });

  const inviteMutation = useMutation({
    mutationFn: inviteDomainAdmin,
    onSuccess: (data: any) => {
      setInviteDialogOpen(false);
      setInviteEmail("");
      setInviteDomainId("");
      queryClient.invalidateQueries({ queryKey: ["domains"] });

      // Email is always queued (background task) — show success + copy URL as fallback
      toast.success(
        `Invitation queued for ${data?.email || "the admin"}. Email will arrive shortly.`,
        { duration: 6000 }
      );
      // Silently copy the invite URL to clipboard so admin has it as a backup
      if (data?.invite_url) {
        navigator.clipboard.writeText(data.invite_url).catch(() => {});
      }
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to send invitation.");
    },
  });

  const handleRegenerateDkim = async (domainId: string) => {
    setDkimLoading(domainId);
    try {
      const result: DkimResult = await regenerateDkim(domainId);
      setDkimResult(result);
      setDkimDialogOpen(true);
      const cfMsg = result.cloudflare === "pushed_to_cloudflare"
        ? " DKIM record pushed to Cloudflare automatically."
        : result.cloudflare === "no_cloudflare_zone"
        ? " Add the TXT record manually (no Cloudflare zone linked)."
        : ` Cloudflare note: ${result.cloudflare}`;
      toast.success(`DKIM key regenerated for ${result.domain}.${cfMsg}`);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to regenerate DKIM key.");
    } finally {
      setDkimLoading(null);
    }
  };

  // ── Handlers
  const handleFormChange = (key: keyof DomainForm, value: string) =>
    setForm((prev) => ({ ...prev, [key]: value }));

  const validateForm = (): string | null => {
    if (!form.name.trim()) return "Domain name is required.";
    if (!/^[a-z0-9.-]+\.[a-z]{2,}$/i.test(form.name.trim()))
      return "Enter a valid domain name (e.g. example.com).";
    if (!form.admin_email.trim()) return "Admin email is required.";
    const emailDomain = form.admin_email.split("@")[1]?.toLowerCase();
    if (emailDomain !== form.name.trim().toLowerCase())
      return `Admin email must belong to this domain (@${form.name.trim()}).`;
    if (!form.admin_password || form.admin_password.length < 8)
      return "Password must be at least 8 characters.";
    if (form.dns_mode === "auto" && !form.cloudflare_token.trim())
      return "Cloudflare API token is required for auto DNS configuration.";
    return null;
  };

  const handleAddDomain = () => {
    const err = validateForm();
    if (err) { toast.warning(err); return; }

    const payload: Record<string, unknown> = {
      name: form.name.trim().toLowerCase(),
      admin_email: form.admin_email.trim().toLowerCase(),
      admin_password: form.admin_password,
      dns_mode: form.dns_mode,
      storage_quota_mb: form.storage_quota_mb ? parseInt(form.storage_quota_mb, 10) : null,
    };
    if (form.dns_mode === "auto") payload.cloudflare_token = form.cloudflare_token.trim();

    addDomainMutation.mutate(payload);
  };

  const handleCloseAddDomain = () => {
    setAddDomainOpen(false);
    setForm(EMPTY_FORM);
    setStep("form");
    setDnsResult(null);
    setShowPassword(false);
  };

  const handleInvite = () => {
    if (!inviteEmail || !inviteDomainId) {
      toast.warning("Please fill out all fields.");
      return;
    }
    inviteMutation.mutate({ email: inviteEmail, domain_id: inviteDomainId });
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard!");
  };

  const filteredDomains = Array.isArray(data) ? data : data?.domains ?? [];

  // ── UI helpers
  const fieldClass =
    "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50";

  return (
    <div className="space-y-4">
      {/* ── Toolbar ── */}
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <Input
            placeholder="Search domains..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-64"
          />
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline">
                Status:{" "}
                {statusFilter.charAt(0).toUpperCase() + statusFilter.slice(1)}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem onSelect={() => setStatusFilter("all")}>All</DropdownMenuItem>
              <DropdownMenuItem onSelect={() => setStatusFilter("active")}>Active</DropdownMenuItem>
              <DropdownMenuItem onSelect={() => setStatusFilter("inactive")}>Inactive</DropdownMenuItem>
              <DropdownMenuItem onSelect={() => setStatusFilter("suspended")}>Suspended</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        <div className="flex items-center space-x-2">
          {/* ── Add Domain ── */}
          <Dialog open={isAddDomainOpen} onOpenChange={(open) => { if (!open) handleCloseAddDomain(); else setAddDomainOpen(true); }}>
            <DialogTrigger asChild>
              <Button variant="outline" id="btn-add-domain">
                <Globe className="mr-2 h-4 w-4" />
                Add Domain
              </Button>
            </DialogTrigger>

            <DialogContent className="sm:max-w-[560px] max-h-[90vh] overflow-y-auto">
              {step === "form" ? (
                <>
                  <DialogHeader>
                    <DialogTitle>Add New Domain</DialogTitle>
                    <DialogDescription>
                      Fill in the details below to onboard a new domain. A domain admin account will be created automatically.
                    </DialogDescription>
                  </DialogHeader>

                  <div className="space-y-5 py-2">
                    {/* Section: Domain */}
                    <div className="space-y-1">
                      <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Domain Details</p>
                      <div className="space-y-3 rounded-md border p-4">
                        <div className="space-y-1.5">
                          <Label htmlFor="nd-name">Domain Name <span className="text-destructive">*</span></Label>
                          <Input
                            id="nd-name"
                            placeholder="example.com"
                            value={form.name}
                            onChange={(e) => handleFormChange("name", e.target.value)}
                          />
                        </div>
                        <div className="space-y-1.5">
                          <Label htmlFor="nd-quota">
                            Storage Quota (MB)
                            <span className="ml-1 text-xs text-muted-foreground">(leave blank for unlimited)</span>
                          </Label>
                          <Input
                            id="nd-quota"
                            type="number"
                            min={100}
                            placeholder="e.g. 10240 for 10 GB"
                            value={form.storage_quota_mb}
                            onChange={(e) => handleFormChange("storage_quota_mb", e.target.value)}
                          />
                        </div>
                      </div>
                    </div>

                    {/* Section: Domain Admin */}
                    <div className="space-y-1">
                      <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Domain Admin Account</p>
                      <div className="space-y-3 rounded-md border p-4">
                        <div className="space-y-1.5">
                          <Label htmlFor="nd-admin-email">
                            Admin Email <span className="text-destructive">*</span>
                          </Label>
                          <Input
                            id="nd-admin-email"
                            type="email"
                            placeholder={form.name ? `admin@${form.name}` : "admin@example.com"}
                            value={form.admin_email}
                            onChange={(e) => handleFormChange("admin_email", e.target.value)}
                          />
                          <p className="text-xs text-muted-foreground flex items-center gap-1">
                            <Info className="h-3 w-3" />
                            Must match the domain above (e.g. name@{form.name || "domain.com"})
                          </p>
                        </div>
                        <div className="space-y-1.5">
                          <Label htmlFor="nd-admin-pass">
                            Initial Password <span className="text-destructive">*</span>
                          </Label>
                          <div className="relative">
                            <Input
                              id="nd-admin-pass"
                              type={showPassword ? "text" : "password"}
                              placeholder="Min. 8 characters"
                              value={form.admin_password}
                              onChange={(e) => handleFormChange("admin_password", e.target.value)}
                              className="pr-10"
                            />
                            <button
                              type="button"
                              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                              onClick={() => setShowPassword((v) => !v)}
                              tabIndex={-1}
                            >
                              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                            </button>
                          </div>
                          <p className="text-xs text-muted-foreground">
                            The domain admin can change this after first login.
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Section: DNS Configuration */}
                    <div className="space-y-1">
                      <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">DNS Configuration</p>
                      <div className="space-y-3 rounded-md border p-4">
                        <div className="space-y-1.5">
                          <Label>DNS Setup Mode <span className="text-destructive">*</span></Label>
                          <div className="flex gap-3">
                            <label
                              className={`flex flex-1 cursor-pointer items-center gap-2 rounded-md border px-3 py-2.5 text-sm transition-colors ${
                                form.dns_mode === "manual"
                                  ? "border-primary bg-primary/10 text-primary"
                                  : "border-input hover:bg-muted"
                              }`}
                            >
                              <input
                                type="radio"
                                name="dns_mode"
                                value="manual"
                                checked={form.dns_mode === "manual"}
                                onChange={() => handleFormChange("dns_mode", "manual")}
                                className="sr-only"
                              />
                              <Globe className="h-4 w-4 shrink-0" />
                              <div>
                                <p className="font-medium">Manual</p>
                                <p className="text-xs text-muted-foreground">I'll configure DNS myself</p>
                              </div>
                            </label>
                            <label
                              className={`flex flex-1 cursor-pointer items-center gap-2 rounded-md border px-3 py-2.5 text-sm transition-colors ${
                                form.dns_mode === "auto"
                                  ? "border-primary bg-primary/10 text-primary"
                                  : "border-input hover:bg-muted"
                              }`}
                            >
                              <input
                                type="radio"
                                name="dns_mode"
                                value="auto"
                                checked={form.dns_mode === "auto"}
                                onChange={() => handleFormChange("dns_mode", "auto")}
                                className="sr-only"
                              />
                              <CheckCircle2 className="h-4 w-4 shrink-0" />
                              <div>
                                <p className="font-medium">Auto (Cloudflare)</p>
                                <p className="text-xs text-muted-foreground">Configure via Cloudflare API</p>
                              </div>
                            </label>
                          </div>
                        </div>

                        {form.dns_mode === "auto" && (
                          <div className="space-y-1.5">
                            <Label htmlFor="nd-cf-token">
                              Cloudflare API Token <span className="text-destructive">*</span>
                            </Label>
                            <Input
                              id="nd-cf-token"
                              type="password"
                              placeholder="Cloudflare API token with DNS Edit permission"
                              value={form.cloudflare_token}
                              onChange={(e) => handleFormChange("cloudflare_token", e.target.value)}
                            />
                            <p className="text-xs text-muted-foreground flex items-center gap-1">
                              <Info className="h-3 w-3" />
                              The domain must already be added to Cloudflare. Token needs Zone:DNS:Edit permission.
                            </p>
                          </div>
                        )}

                        {form.dns_mode === "manual" && (
                          <p className="text-xs text-muted-foreground flex items-center gap-1">
                            <Info className="h-3 w-3" />
                            After creation, DNS records will be shown for you to configure.
                          </p>
                        )}
                      </div>
                    </div>
                  </div>

                  <DialogFooter>
                    <Button variant="outline" onClick={handleCloseAddDomain}>
                      Cancel
                    </Button>
                    <Button
                      id="btn-add-domain-submit"
                      onClick={handleAddDomain}
                      disabled={addDomainMutation.isPending}
                    >
                      {addDomainMutation.isPending
                        ? form.dns_mode === "auto"
                          ? "Creating & Configuring DNS..."
                          : "Creating..."
                        : "Create Domain"}
                    </Button>
                  </DialogFooter>
                </>
              ) : (
                /* ── Step 2: DNS Result ── */
                <>
                  <DialogHeader>
                    <DialogTitle className="flex items-center gap-2">
                      <CheckCircle2 className="h-5 w-5 text-green-500" />
                      Domain Created Successfully
                    </DialogTitle>
                    <DialogDescription>
                      <strong>{dnsResult?.domain.name}</strong> has been added.
                      {dnsResult?.dns_mode === "auto" && !dnsResult.cloudflare_error
                        ? " DNS has been auto-configured via Cloudflare."
                        : " Configure the DNS records below manually."}
                    </DialogDescription>
                  </DialogHeader>

                  <div className="space-y-4 py-2">
                    {/* Summary */}
                    <div className="rounded-md border p-4 space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Domain</span>
                        <span className="font-medium">{dnsResult?.domain.name}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Admin Email</span>
                        <span className="font-medium">{dnsResult?.admin_email}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">DNS Status</span>
                        <Badge variant={dnsResult?.domain.is_verified ? "default" : "secondary"}>
                          {dnsResult?.domain.is_verified ? "Verified" : "Pending"}
                        </Badge>
                      </div>
                      {dnsResult?.domain.storage_quota_mb && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Storage Quota</span>
                          <span className="font-medium">
                            {dnsResult.domain.storage_quota_mb >= 1024
                              ? `${(dnsResult.domain.storage_quota_mb / 1024).toFixed(1)} GB`
                              : `${dnsResult.domain.storage_quota_mb} MB`}
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Cloudflare error */}
                    {dnsResult?.cloudflare_error && (
                      <div className="rounded-md border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive">
                        <p className="font-medium mb-1">Cloudflare DNS setup failed</p>
                        <p>{dnsResult.cloudflare_error}</p>
                        <p className="mt-2 text-muted-foreground">Please configure DNS records manually below.</p>
                      </div>
                    )}

                    {/* Manual DNS records */}
                    {dnsResult?.dns_records && dnsResult.dns_records.length > 0 && (
                      <div className="space-y-2">
                        <p className="text-sm font-medium">Required DNS Records</p>
                        <p className="text-xs text-muted-foreground">Add these records in your DNS provider:</p>
                        <div className="space-y-2">
                          {dnsResult.dns_records.map((record, i) => (
                            <div key={i} className="rounded-md border bg-muted/40 p-3 text-xs font-mono">
                              <div className="flex items-center justify-between mb-1">
                                <Badge variant="outline" className="text-[10px]">{record.type}</Badge>
                                <button
                                  onClick={() => copyToClipboard(record.value)}
                                  className="text-muted-foreground hover:text-foreground"
                                  title="Copy value"
                                >
                                  <Copy className="h-3.5 w-3.5" />
                                </button>
                              </div>
                              <p><span className="text-muted-foreground">Name: </span>{record.name}</p>
                              <p className="break-all"><span className="text-muted-foreground">Value: </span>{record.value}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Auto-DNS success */}
                    {dnsResult?.dns_mode === "auto" && !dnsResult.cloudflare_error && (
                      <div className="rounded-md border border-green-500/30 bg-green-500/10 p-3 text-sm text-green-700 dark:text-green-400">
                        <p className="font-medium flex items-center gap-1.5">
                          <CheckCircle2 className="h-4 w-4" />
                          All DNS records configured automatically via Cloudflare
                        </p>
                        {dnsResult.domain.cloudflare_zone_id && (
                          <p className="mt-1 text-xs text-muted-foreground">
                            Zone ID: {dnsResult.domain.cloudflare_zone_id}
                          </p>
                        )}
                      </div>
                    )}
                  </div>

                  <DialogFooter>
                    <Button onClick={handleCloseAddDomain}>Done</Button>
                  </DialogFooter>
                </>
              )}
            </DialogContent>
          </Dialog>

          {/* ── Invite Domain Admin ── */}
          <Dialog open={isInviteDialogOpen} onOpenChange={setInviteDialogOpen}>
            <DialogTrigger asChild>
              <Button id="btn-invite-domain-admin">
                <PlusCircle className="mr-2 h-4 w-4" />
                Invite Domain Admin
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Invite New Domain Admin</DialogTitle>
                <DialogDescription>
                  Send an invitation to a new administrator to manage a domain.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="invite-domain">Domain</Label>
                  <select
                    id="invite-domain"
                    value={inviteDomainId}
                    onChange={(e) => setInviteDomainId(e.target.value)}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  >
                    <option value="">-- Select a domain --</option>
                    {filteredDomains.map((d: any) => (
                      <option key={d.id} value={d.id}>
                        {d.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="invite-email">Admin Email</Label>
                  <Input
                    id="invite-email"
                    type="email"
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    placeholder="admin@example.com"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setInviteDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleInvite} disabled={inviteMutation.isPending}>
                  {inviteMutation.isPending ? "Sending..." : "Send Invitation"}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* ── Domains Table ── */}
      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Domain</TableHead>
              <TableHead>Admin</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Users</TableHead>
              <TableHead>Storage</TableHead>
              <TableHead>Created At</TableHead>
              <TableHead>
                <span className="sr-only">Actions</span>
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && (
              <TableRow>
                <TableCell colSpan={7}>Loading...</TableCell>
              </TableRow>
            )}
            {error && (
              <TableRow>
                <TableCell colSpan={7}>Error loading domains.</TableCell>
              </TableRow>
            )}
            {filteredDomains?.map((domain: any) => (
              <TableRow key={domain.id}>
                <TableCell className="font-medium">{domain.name}</TableCell>
                <TableCell>{domain.admin_email ?? "—"}</TableCell>
                <TableCell>
                  <Badge
                    variant={
                      domain.is_suspended
                        ? "destructive"
                        : domain.is_verified
                          ? "default"
                          : "secondary"
                    }
                  >
                    {domain.is_suspended
                      ? "Suspended"
                      : domain.is_verified
                        ? "Active"
                        : "Pending DNS"}
                  </Badge>
                </TableCell>
                <TableCell>{domain.user_count ?? "—"}</TableCell>
                <TableCell>
                  {domain.storage_quota_mb
                    ? domain.storage_quota_mb >= 1024
                      ? `${(domain.storage_quota_mb / 1024).toFixed(1)} GB`
                      : `${domain.storage_quota_mb} MB`
                    : "Unlimited"}
                </TableCell>
                <TableCell>
                  {new Date(domain.created_at).toLocaleDateString()}
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
                        <DropdownMenuItem>View Details</DropdownMenuItem>
                        <DropdownMenuItem>
                          {domain.is_suspended ? "Unsuspend Domain" : "Suspend Domain"}
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onSelect={() => handleRegenerateDkim(domain.id)}
                          disabled={dkimLoading === domain.id}
                          className="flex items-center gap-2"
                        >
                          {dkimLoading === domain.id
                            ? <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                            : <KeyRound className="h-3.5 w-3.5" />}
                          Regenerate DKIM Key
                        </DropdownMenuItem>
                        <DropdownMenuItem className="text-red-600">
                          Delete Domain
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      {/* ── DKIM Result Dialog ── */}
      <DkimResultDialog
        open={dkimDialogOpen}
        onClose={() => { setDkimDialogOpen(false); setDkimResult(null); }}
        result={dkimResult}
      />
    </div>
  );
}

// ── DKIM Result Dialog (rendered outside the table for clean portal) ──────────
function DkimResultDialog({
  open,
  onClose,
  result,
}: {
  open: boolean;
  onClose: () => void;
  result: DkimResult | null;
}) {
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied!");
  };
  if (!result) return null;
  const cfOk = result.cloudflare === "pushed_to_cloudflare";
  return (
    <Dialog open={open} onOpenChange={(o) => { if (!o) onClose(); }}>
      <DialogContent className="sm:max-w-[540px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <KeyRound className="h-5 w-5 text-primary" />
            DKIM Key Generated — {result.domain}
          </DialogTitle>
          <DialogDescription>
            A new RSA-2048 DKIM key pair has been generated. The private key is
            saved on the mail server. Add the TXT record below to your DNS.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-2">
          {/* Cloudflare status */}
          <div className={`rounded-md border p-3 text-sm ${
            cfOk
              ? "border-green-500/30 bg-green-500/10 text-green-700 dark:text-green-400"
              : "border-amber-500/30 bg-amber-500/10 text-amber-700 dark:text-amber-400"
          }`}>
            {cfOk ? (
              <p className="flex items-center gap-1.5 font-medium">
                <CheckCircle2 className="h-4 w-4" />
                DKIM TXT record automatically added to Cloudflare
              </p>
            ) : (
              <p className="flex items-center gap-1.5 font-medium">
                <Info className="h-4 w-4" />
                {result.cloudflare === "no_cloudflare_zone"
                  ? "No Cloudflare zone linked — add the record manually below"
                  : result.cloudflare}
              </p>
            )}
          </div>

          {/* DNS record */}
          <div className="space-y-1">
            <p className="text-sm font-medium">DNS TXT Record</p>
            <div className="rounded-md border bg-muted/40 p-3 text-xs font-mono space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Type</span>
                <Badge variant="outline">TXT</Badge>
              </div>
              <div className="flex items-start justify-between gap-2">
                <span className="text-muted-foreground shrink-0">Name</span>
                <span className="break-all text-right">{result.dns_record.name}</span>
              </div>
              <div className="flex items-start justify-between gap-2">
                <span className="text-muted-foreground shrink-0">Value</span>
                <div className="flex items-start gap-1">
                  <span className="break-all text-right max-w-[340px]">{result.dns_record.value}</span>
                  <button
                    onClick={() => copyToClipboard(result.dns_record.value)}
                    className="text-muted-foreground hover:text-foreground shrink-0 mt-0.5"
                    title="Copy value"
                  >
                    <Copy className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-md border border-blue-500/30 bg-blue-500/10 p-3 text-xs text-blue-700 dark:text-blue-400 space-y-1">
            <p className="font-medium">After adding this record:</p>
            <p>• Emails from <strong>{result.domain}</strong> will show <code className="bg-blue-500/10 px-1 rounded">signed-by: {result.domain}</code></p>
            <p>• DNS propagation can take up to 24 hours</p>
            <p>• Use <strong>Verify DNS</strong> in the domain admin panel to confirm</p>
          </div>
        </div>

        <DialogFooter>
          <Button onClick={onClose}>Done</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
