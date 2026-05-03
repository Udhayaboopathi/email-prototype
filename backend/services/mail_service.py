import asyncio
import email
import mailbox
from datetime import UTC, datetime
from email.message import EmailMessage
from pathlib import Path
from uuid import uuid4

from config import get_settings
from schemas.mail import EmailItem, EmailSendRequest
from smtp.outbound import OutboundSMTPClient


class MailService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.outbound = OutboundSMTPClient()

    def _maildir_path(self, mailbox_address: str) -> Path:
        return Path(self.settings.maildir_base) / mailbox_address.replace("@", "_at_")

    async def store_inbound(self, mail_from: str, rcpt_tos: list[str], subject: str, raw_message: bytes) -> None:
        async def _write() -> None:
            for rcpt in rcpt_tos:
                path = self._maildir_path(rcpt)
                md = mailbox.Maildir(path, create=True)
                md.add(raw_message)
                md.flush()

        await asyncio.to_thread(_write)

    async def send(self, payload: EmailSendRequest) -> str:
        msg = EmailMessage()
        msg["From"] = payload.from_email
        msg["To"] = ", ".join(payload.to)
        if payload.cc:
            msg["Cc"] = ", ".join(payload.cc)
        msg["Subject"] = payload.subject
        msg["Date"] = email.utils.format_datetime(datetime.now(UTC))
        msg["Message-ID"] = email.utils.make_msgid()
        msg.set_content(payload.body_text or payload.body_html)
        msg.add_alternative(payload.body_html, subtype="html")
        recipients = [*payload.to, *payload.cc, *payload.bcc]
        await self.outbound.send_direct_mx(msg, payload.from_email, recipients)
        return msg["Message-ID"]

    async def list_folder(self, mailbox_address: str, folder: str = "INBOX") -> list[EmailItem]:
        def _read() -> list[EmailItem]:
            path = self._maildir_path(mailbox_address)
            md = mailbox.Maildir(path, create=True)
            items: list[EmailItem] = []
            for key, message in md.iteritems():
                to_header = message.get("to", "")
                to_values = [value.strip() for value in to_header.split(",") if value.strip()]
                items.append(
                    EmailItem(
                        uid=key,
                        folder=folder,
                        subject=message.get("subject", "(no subject)"),
                        from_email=message.get("from", ""),
                        to=to_values,
                        date=datetime.now(UTC),
                        seen=False,
                        snippet=(message.get_payload(decode=False) or "")[:200],
                    )
                )
            return items

        return await asyncio.to_thread(_read)

    async def append_sent(self, mailbox_address: str, msg: EmailMessage) -> str:
        uid = f"{int(datetime.now(UTC).timestamp())}.{uuid4().hex}"

        def _append() -> None:
            path = self._maildir_path(mailbox_address)
            md = mailbox.Maildir(path, create=True)
            md.add(msg.as_bytes())
            md.flush()

        await asyncio.to_thread(_append)
        return uid
