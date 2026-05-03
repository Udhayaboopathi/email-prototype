from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from imap.session import IMAPSession


async def handle(session: IMAPSession, tag: str, args: list[str]) -> str:
    if session.state != "SELECTED":
        return f"{tag} NO SELECT mailbox first\r\n"
    return f"{tag} OK STORE completed\r\n"
