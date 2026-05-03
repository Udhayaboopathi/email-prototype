export type UserRole = "user" | "domain_admin" | "super_admin";

// Alias for Role used in auth lib
export type Role = UserRole;

export interface TokenPair {
  access_token: string;
  refresh_token: string;
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  is_active: boolean;
  last_login: string | null;
  avatar_url?: string;
  domain_id?: string;
  domain?: string;
  totp_enabled: boolean;
}

export interface Whitelabel {
  company_name: string | null;
  primary_color: string | null;
  logo_url: string | null;
}

export interface MailItem {
  id: string;
  uid: string;
  thread_id?: string;
  subject: string;
  from: string;
  from_email: string;
  to: string[];
  date: string;
  snippet: string;
  body: string;
  html?: string;
  is_read: boolean;
  is_starred: boolean;
  folder: string;
  labels?: string[];
  priority_score?: number;
  has_attachments?: boolean;
  attachments?: Attachment[];
}

export interface Attachment {
  id: string;
  filename: string;
  size: number;
  content_type: string;
  url?: string;
}

export interface Domain {
  id: string;
  name: string;
  is_verified: boolean;
  is_active?: boolean;
  is_suspended?: boolean;
  created_at: string;
  user_count?: number;
  mailbox_count?: number;
  storage_used_gb?: number;
  storage_quota_gb?: number;
  admin_email?: string;
  whitelabel_company_name?: string;
  whitelabel_primary_color?: string;
  whitelabel_logo_url?: string;
}

export interface Mailbox {
  id: string;
  email: string;
  address?: string;
  quota_mb?: number;
  storage_used_gb?: number;
  storage_limit_gb?: number;
  is_active?: boolean;
  last_login?: string | null;
  user?: User;
}

export interface ApiKey {
  id: string;
  name: string;
  scopes?: string[];
  prefix?: string;
  last_used_at: string | null;
  expires_at?: string | null;
  created_at: string;
  key?: string; // Only available on creation
}

export interface AuditLog {
  id: string;
  user_id?: string;
  user?: User | null;
  action: string;
  target?: string;
  details?: string;
  ip_address?: string;
  created_at: string;
}

export interface BackupJob {
  id: string;
  status: "pending" | "running" | "completed" | "failed";
  type?: "full" | "domain";
  created_at: string;
  completed_at: string | null;
  file_path?: string | null;
  file_size_gb: number | null;
}

export interface DnsRecord {
  type: string;
  name: string;
  value: string;
  ttl?: string;
  priority?: string;
  purpose?: string;
  status?: "valid" | "invalid" | "pending";
  details?: string;
}

export interface Label {
  id: string;
  name: string;
  color: string;
  email_count?: number;
}

export interface EmailRule {
  id: string;
  name: string;
  is_enabled: boolean;
  match_type: "any" | "all";
  conditions: RuleCondition[];
  actions: RuleAction[];
  priority?: number;
}

export interface RuleCondition {
  field: string;
  operator: string;
  value: string;
}

export interface RuleAction {
  type: string;
  value?: string;
}

export interface EmailTemplate {
  id: string;
  name: string;
  subject: string;
  body: string;
  created_at: string;
  updated_at?: string;
}

export interface Webhook {
  id: string;
  url: string;
  secret?: string;
  events: string[];
  is_active?: boolean;
  last_triggered_at?: string | null;
  failure_count?: number;
  created_at: string;
}

export interface CalendarEvent {
  id: string;
  title: string;
  start: string;
  end: string;
  all_day?: boolean;
  location?: string;
  description?: string;
  attendees?: string[];
}

export interface Task {
  id: string;
  title: string;
  description?: string;
  is_complete: boolean;
  priority?: "high" | "normal" | "low";
  due_date?: string | null;
  linked_email_id?: string | null;
  created_at: string;
}

export interface Note {
  id: string;
  title: string;
  body: string;
  linked_email_id?: string | null;
  created_at: string;
  updated_at?: string;
}

export interface SharedMailbox {
  id: string;
  display_name: string;
  address: string;
  members?: SharedMailboxMember[];
}

export interface SharedMailboxMember {
  id: string;
  email: string;
  permission: "read_only" | "read_write" | "admin";
}

export interface LoginActivity {
  id: string;
  ip_address: string | null;
  country?: string | null;
  user_agent?: string | null;
  success?: string;
  created_at: string | null;
}
