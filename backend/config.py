from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    server_ip: str = Field(alias="SERVER_IP")
    smtp_hostname: str = Field(alias="SMTP_HOSTNAME")
    database_url: str = Field(alias="DATABASE_URL")
    postgres_db: str = Field(alias="POSTGRES_DB")
    postgres_user: str = Field(alias="POSTGRES_USER")
    postgres_password: str = Field(alias="POSTGRES_PASSWORD")
    redis_url: str = Field(alias="REDIS_URL")
    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=30, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    encryption_secret_key: str = Field(alias="ENCRYPTION_SECRET_KEY")
    maildir_base: str = Field(default="/var/mail", alias="MAILDIR_BASE")
    max_message_size_mb: int = Field(default=25, alias="MAX_MESSAGE_SIZE_MB")
    dkim_selector: str = Field(default="mail", alias="DKIM_SELECTOR")
    cloudflare_api_token: str | None = Field(default=None, alias="CLOUDFLARE_API_TOKEN")
    backup_passphrase: str | None = Field(default=None, alias="BACKUP_PASSPHRASE")
    backup_retention_days: int = Field(default=7, alias="BACKUP_RETENTION_DAYS")
    backup_schedule_hour: int = Field(default=2, alias="BACKUP_SCHEDULE_HOUR")
    super_admin_email: str = Field(alias="SUPER_ADMIN_EMAIL")
    super_admin_password: str = Field(alias="SUPER_ADMIN_PASSWORD")
    frontend_url: str = Field(alias="FRONTEND_URL")
    invite_base_url: str = Field(alias="INVITE_BASE_URL")
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    ai_summary_enabled: bool = Field(default=True, alias="AI_SUMMARY_ENABLED")
    ai_smart_reply_enabled: bool = Field(default=True, alias="AI_SMART_REPLY_ENABLED")
    ai_priority_inbox_enabled: bool = Field(default=True, alias="AI_PRIORITY_INBOX_ENABLED")
    tracking_base_url: str = Field(alias="TRACKING_BASE_URL")
    tracking_enabled: bool = Field(default=True, alias="TRACKING_ENABLED")
    spamassassin_host: str = Field(default="spamassassin", alias="SPAMASSASSIN_HOST")
    clamav_host: str = Field(default="clamav", alias="CLAMAV_HOST")
    next_public_api_url: str = Field(alias="NEXT_PUBLIC_API_URL")


@lru_cache
def get_settings() -> Settings:
    return Settings()
