from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from imap.session import IMAPSession



async def handle(session: IMAPSession, tag: str, args: list[str]) -> str:
    if session.state == "NONAUTH":
        return f"{tag} NO Authenticate first\r\n"
    return f"{tag} OK APPEND completed\r\n"
