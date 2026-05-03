from email.message import EmailMessage

from tasks.celery_app import celery_app
from smtp.outbound import OutboundSMTPClient


@celery_app.task(name="tasks.delivery.deliver_direct")
def deliver_direct(envelope_from: str, recipients: list[str], subject: str, body_html: str) -> str:
    import asyncio

    async def _send() -> None:
        msg = EmailMessage()
        msg["From"] = envelope_from
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject
        msg.set_content(body_html)
        msg.add_alternative(body_html, subtype="html")
        await OutboundSMTPClient().send_direct_mx(msg, envelope_from, recipients)

    asyncio.run(_send())
    return "queued"
