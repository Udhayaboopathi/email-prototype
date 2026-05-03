import asyncio
import email
import mailbox as py_mailbox
from dataclasses import dataclass
from email import policy
from email.parser import BytesParser
from pathlib import Path

import dkim
from sqlalchemy import select

from config import get_settings
from core.security import verify_password
from database import async_session_factory
from models.alias import Alias
from models.domain import Domain
from models.mailbox import Mailbox
from models.user import User
from services.rules_service import RulesService


@dataclass
class SMTPValidationResult:
    accepted: bool
    response: str
    folder: str = "INBOX"


class InboundSMTPHandler:
    async def verify_submission_auth(self, username: str, password: str, _settings) -> bool:
        async with async_session_factory() as db:
            mailbox = await db.scalar(select(Mailbox).where((Mailbox.address == username) & (Mailbox.is_active.is_(True))))
            if not mailbox:
                return False
            user = await db.scalar(select(User).where(User.id == mailbox.user_id))
            if not user:
                return False
            hashed = getattr(user, "hashed_password", None) or getattr(user, "password_hash", None)
            if not hashed:
                return False
            return verify_password(password, hashed)

    async def _domain_for_recipient(self, recipient: str) -> tuple[str, str] | None:
        if "@" not in recipient:
            return None
        local, domain_name = recipient.split("@", 1)
        async with async_session_factory() as db:
            domain = await db.scalar(select(Domain).where(Domain.name == domain_name))
            if not domain:
                return None
            if getattr(domain, "is_suspended", False):
                return ("", "__SUSPENDED__")
            alias = await db.scalar(select(Alias).where((Alias.source_address == recipient) & (Alias.is_active.is_(True))))
            if alias:
                destination = getattr(alias, "destination_address", "")
                if "@" in destination:
                    local, domain_name = destination.split("@", 1)
            elif hasattr(Alias, "is_catch_all"):
                catch_all = await db.scalar(
                    select(Alias).where((Alias.domain_id == getattr(domain, "id")) & (Alias.is_catch_all.is_(True)) & (Alias.is_active.is_(True)))
                )
                if catch_all:
                    destination = getattr(catch_all, "destination_address", "")
                    if "@" in destination:
                        local, domain_name = destination.split("@", 1)
            return (local, domain_name)

    async def _run_spamc(self, raw: bytes) -> tuple[float, str]:
        settings = get_settings()
        process = await asyncio.create_subprocess_exec(
            "spamc",
            "-d",
            settings.spamassassin_host,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await process.communicate(raw)
        text = stdout.decode("utf-8", errors="ignore")
        score = 0.0
        for line in text.splitlines():
            if line.startswith("X-Spam-Score:"):
                try:
                    score = float(line.split(":", 1)[1].strip())
                except ValueError:
                    score = 0.0
        status = "Yes" if score > 5 else "No"
        return score, status

    async def _clamav_scan(self, raw: bytes) -> bool:
        process = await asyncio.create_subprocess_exec(
            "clamdscan",
            "--stream",
            "-",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await process.communicate(raw)
        return b"FOUND" in stdout

    async def _verify_dkim(self, raw: bytes) -> bool:
        try:
            return dkim.verify(raw)
        except Exception:
            return False

    async def _write_maildir(self, domain_name: str, local_part: str, folder: str, raw: bytes) -> Path:
        settings = get_settings()
        mailbox_root = Path(settings.maildir_base) / domain_name / local_part
        box = py_mailbox.Maildir(mailbox_root.as_posix(), create=True)
        if folder != "INBOX":
            box.add_folder(folder)
            folder_box = box.get_folder(folder)
            key = folder_box.add(raw)
            message_path = mailbox_root / f".{folder}" / "new" / str(key)
        else:
            key = box.add(raw)
            message_path = mailbox_root / "new" / str(key)
        return message_path

    async def _update_usage(self, recipient: str, size_mb: float) -> None:
        async with async_session_factory() as db:
            mailbox = await db.scalar(select(Mailbox).where(Mailbox.address == recipient))
            if mailbox and hasattr(mailbox, "used_mb"):
                mailbox.used_mb = float(getattr(mailbox, "used_mb", 0.0) or 0.0) + size_mb
                await db.commit()

    async def _apply_post_processing(self, recipient: str, parsed_message: email.message.EmailMessage, folder: str) -> None:
        async with async_session_factory() as db:
            mailbox = await db.scalar(select(Mailbox).where(Mailbox.address == recipient))
            if not mailbox:
                return
            rules_service = RulesService(db)
            await rules_service.apply_rules(mailbox.id, parsed_message)

    async def _validate(self, envelope) -> SMTPValidationResult:  # type: ignore[no-untyped-def]
        settings = get_settings()
        if len(envelope.content) > settings.max_message_size_mb * 1024 * 1024:
            return SMTPValidationResult(False, "552 Message exceeds size limit")

        for recipient in envelope.rcpt_tos:
            resolution = await self._domain_for_recipient(recipient)
            if resolution is None:
                return SMTPValidationResult(False, "550 Unknown recipient domain")
            if resolution[1] == "__SUSPENDED__":
                return SMTPValidationResult(False, "451 Domain temporarily suspended")

        spam_score, spam_status = await self._run_spamc(envelope.content)
        if await self._clamav_scan(envelope.content):
            return SMTPValidationResult(False, "550 Virus detected")

        folder = "Spam" if spam_score > 10 else "INBOX"
        message = BytesParser(policy=policy.default).parsebytes(envelope.content)
        message["X-Spam-Score"] = str(spam_score)
        message["X-Spam-Status"] = spam_status
        if not await self._verify_dkim(envelope.content):
            message["X-DKIM-Result"] = "fail"
        envelope.content = message.as_bytes()

        return SMTPValidationResult(True, "250 Message accepted", folder=folder)

    async def handle_DATA(self, server, session, envelope):  # type: ignore[no-untyped-def]
        validation = await self._validate(envelope)
        if not validation.accepted:
            return validation.response

        parsed = BytesParser(policy=policy.default).parsebytes(envelope.content)
        size_mb = len(envelope.content) / (1024 * 1024)

        for recipient in envelope.rcpt_tos:
            resolved = await self._domain_for_recipient(recipient)
            if not resolved:
                continue
            local, domain_name = resolved
            await self._write_maildir(domain_name, local, validation.folder, envelope.content)
            await self._update_usage(recipient, size_mb)
            await self._apply_post_processing(recipient, parsed, validation.folder)

        return validation.response
