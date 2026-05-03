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
}

export interface Whitelabel {
  company_name: string;
  primary_color: string;
  logo_url: string;
}

export interface MailItem {
  id: string;
  uid: string;           // IMAP UID used as React key
  subject: string;
  from: string;
  from_email: string;    // Sender email address
  to: string[];
  date: string;
  snippet: string;       // Short preview text
  body: string;
  html?: string;
  is_read: boolean;
  is_starred: boolean;
  folder: string;
  attachments?: Attachment[];
}

export interface Attachment {
  id: string;
  filename: string;
  size: number;
  content_type: string;
}

export interface Domain {
  id: string;
  name: string;
  is_active: boolean;
  created_at: string;
  user_count: number;
}

export interface Mailbox {
  id: string;
  email: string;
  user: User;
  storage_used_gb: number;
  storage_limit_gb: number;
}

export interface ApiKey {
  id: string;
  name: string;
  created_at: string;
  last_used_at: string | null;
  key?: string; // Only available on creation
}

export interface AuditLog {
  id: string;
  user: User | null;
  action: string;
  details: string;
  created_at: string;
}

export interface BackupJob {
  id: string;
  status: "pending" | "running" | "completed" | "failed";
  created_at: string;
  completed_at: string | null;
  file_size_gb: number | null;
}

export interface DnsRecord {
  name: string;
  type: string;
  value: string;
  status: "valid" | "invalid" | "pending";
  details: string;
}
