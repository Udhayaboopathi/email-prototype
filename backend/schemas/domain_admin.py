from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, conint, constr


class DomainAdminStats(BaseModel):
    domain_name: str
    storage_quota_gb: int
    used_storage_gb: float
    storage_percent: float
    storage_status: str
    total_mailboxes: int
    active_mailboxes: int
    inactive_mailboxes: int
    dns_verified: bool
    dns_verified_at: Optional[datetime]
    whitelabel_enabled: bool
    ediscovery_enabled: bool
    retention_days: int
    total_aliases: int
    total_shared_mailboxes: int
    emails_sent_today: int
    emails_received_today: int
    last_backup_at: Optional[datetime]
    next_backup_at: Optional[datetime]


class OnboardingStep(BaseModel):
    key: str
    title: str
    description: str
    completed: bool
    action_url: str


class OnboardingStatus(BaseModel):
    steps: List[OnboardingStep]
    all_completed: bool
    completed_count: int
    total_count: int


class MailboxListItem(BaseModel):
    id: str
    full_address: str
    local_part: str
    quota_mb: int
    used_mb: int
    used_percent: float
    storage_status: str
    is_active: bool
    last_login_at: Optional[datetime]
    created_at: datetime
    has_autoresponder: bool = False
    alias_count: int = 0
    rules_count: int = 0


class MailboxCreate(BaseModel):
    local_part: constr(
        min_length=1, max_length=64,
        regex=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,62}[a-zA-Z0-9]$"
    )
    password: constr(min_length=8)
    quota_mb: Optional[conint(ge=0)] = Field(default=1024)
    display_name: Optional[str] = None


class MailboxUpdate(BaseModel):
    quota_mb: Optional[conint(ge=0)] = None
    is_active: Optional[bool] = None
    display_name: Optional[str] = None


class MailboxExportOptions(BaseModel):
    mbox_url: Optional[str]
    zip_url: Optional[str]


class MailboxImportResult(BaseModel):
    imported: int
    failed: int
    skipped_duplicates: Optional[int] = 0


class AliasListItem(BaseModel):
    id: str
    source_address: str
    destination_address: str
    is_active: bool
    is_catch_all: bool
    created_at: datetime


class AliasCreate(BaseModel):
    local_part: Optional[constr(max_length=64)] = Field(default="")
    destination_address: EmailStr
    is_catch_all: Optional[bool] = False


class AliasUpdate(BaseModel):
    destination_address: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class DNSRecord(BaseModel):
    expected: str
    actual: Optional[str]
    valid: bool


class DNSStatus(BaseModel):
    domain_name: str
    server_ip: str
    records: dict[str, DNSRecord]
    all_valid: bool
    last_checked: Optional[datetime]


class DNSGuideResponse(BaseModel):
    records: List[dict]


class BackupJob(BaseModel):
    id: str
    type: Optional[str]
    status: str
    file_size_mb: Optional[int]
    total_messages: Optional[int]
    created_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]


class BackupRestorePreview(BaseModel):
    mailboxes_found: List[str]
    messages_count: int
    aliases_count: int


class BackupRestoreResult(BaseModel):
    mailboxes_restored: int
    messages_restored: int
    aliases_restored: int


class SharedMailboxMemberAdd(BaseModel):
    email: EmailStr
    permission: constr(regex=r"^(read_only|read_write|admin)$")


class SharedMailboxDetail(BaseModel):
    id: str
    display_name: Optional[str]
    full_address: str
    member_count: int
    members: List[dict]
    created_at: datetime


class SharedMailboxCreate(BaseModel):
    local_part: constr(min_length=1, max_length=64)
    display_name: Optional[str]


class WhitelabelSettings(BaseModel):
    logo_url: Optional[str]
    primary_color: Optional[str]
    company_name: Optional[str]
    login_page_preview_url: Optional[str]


class WhitelabelUpdate(BaseModel):
    logo_url: Optional[str]
    primary_color: Optional[constr(regex=r"^#([A-Fa-f0-9]{6})$")]
    company_name: Optional[constr(max_length=100)]


class EdiscoverySearchBody(BaseModel):
    from_address: Optional[EmailStr] = None
    to_address: Optional[EmailStr] = None
    subject_contains: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    mailbox_ids: Optional[List[str]] = None
    include_spam: Optional[bool] = False
    include_trash: Optional[bool] = False


class EdiscoveryExportItem(BaseModel):
    export_id: str
    status: str
    created_at: datetime


class RetentionPolicy(BaseModel):
    retention_days: int
    affected_mailboxes: int
    estimated_emails_to_delete: int
    next_cleanup_at: Optional[datetime]


class RetentionUpdate(BaseModel):
    retention_days: conint(ge=0)


class AuditLogItem(BaseModel):
    id: str
    action: str
    target: Optional[str]
    user_email: Optional[EmailStr]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
