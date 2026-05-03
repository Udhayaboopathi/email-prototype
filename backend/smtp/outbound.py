import asyncio
import uuid
from email.message import EmailMessage

import aiosmtplib
import dns.asyncresolver
from sqlalchemy import and_, select

from database import async_session_factory
from models.unsubscribe import Unsubscribe
from smtp.dkim import sign_message


class OutboundSMTPClient:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries

    async def _resolve_mx(self, recipient: str) -> list[tuple[int, str]]:
        domain = recipient.split("@", 1)[1]
        answers = await dns.asyncresolver.resolve(domain, "MX")
        return sorted([(int(answer.preference), str(answer.exchange).rstrip(".")) for answer in answers], key=lambda x: x[0])

    async def _recipient_unsubscribed(self, from_address: str, recipient: str) -> bool:
        async with async_session_factory() as db:
            row = await db.scalar(
                select(Unsubscribe).where(
                    and_(
                        Unsubscribe.sender_email == from_address,
                        Unsubscribe.recipient_email == recipient,
                        Unsubscribe.is_unsubscribed.is_(True),
                    )
                )
            )
            return row is not None

    async def send_direct_mx(self, message: EmailMessage, envelope_from: str, recipients: list[str]) -> list[str]:
        domain = envelope_from.split("@", 1)[1]
        signed_message = sign_message(message.as_bytes(), domain)
        failed: list[str] = []

        for recipient in recipients:
            if await self._recipient_unsubscribed(envelope_from, recipient):
                failed.append(recipient)
                continue
            delivered = False
            mx_records = await self._resolve_mx(recipient)
            for _, mx_host in mx_records:
                for attempt in range(1, self.max_retries + 1):
                    try:
                        await aiosmtplib.send(
                            signed_message,
                            hostname=mx_host,
                            port=25,
                            sender=envelope_from,
                            recipients=[recipient],
                            timeout=30,
                            start_tls=True,
                        )
                        delivered = True
                        break
                    except Exception:
                        if attempt == self.max_retries:
                            await asyncio.sleep(0)
                        else:
                            await asyncio.sleep(2**attempt)
                if delivered:
                    break
            if not delivered:
                failed.append(recipient)
        return failed


async def send_direct(
    from_address: str,
    to_addresses: list[str],
    subject: str,
    body_text: str,
    body_html: str | None = None,
    attachments: list[dict[str, str]] | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, object]:
    message = EmailMessage()
    message["From"] = from_address
    message["To"] = ", ".join(to_addresses)
    message["Subject"] = subject
    message["Message-ID"] = f"<{uuid.uuid4()}@{from_address.split('@', 1)[1]}>"

    if headers:
        for key, value in headers.items():
            message[key] = value

    if body_html:
        message.set_content(body_text)
        message.add_alternative(body_html, subtype="html")
    else:
        message.set_content(body_text)

    for attachment in attachments or []:
        content = attachment.get("content", "").encode("utf-8")
        filename = attachment.get("filename", "attachment.txt")
        message.add_attachment(content, maintype="application", subtype="octet-stream", filename=filename)

    client = OutboundSMTPClient()
    failed = await client.send_direct_mx(message, from_address, to_addresses)
    return {
        "success": len(failed) == 0,
        "message_id": message["Message-ID"],
        "failed_recipients": failed,
    }
