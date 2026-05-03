import asyncio
import ssl

from imap.session import IMAPSession


async def _handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    session = IMAPSession(reader=reader, writer=writer)
    await session.run()


def _tls_context() -> ssl.SSLContext:
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    try:
        context.load_cert_chain("/etc/ssl/mail.crt", "/etc/ssl/mail.key")
    except Exception:
        context.load_cert_chain("/etc/ssl/mail/fullchain.pem", "/etc/ssl/mail/privkey.pem")
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    return context


async def create_imap_server() -> None:
    server = await asyncio.start_server(_handle_client, host="0.0.0.0", port=993, ssl=_tls_context())
    async with server:
        await server.serve_forever()
