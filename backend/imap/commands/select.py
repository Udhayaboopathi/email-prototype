from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from imap.session import IMAPSession


async def handle(session: IMAPSession, tag: str, args: list[str]) -> str:
    if session.state == "NONAUTH":
        return f"{tag} NO Authenticate first\r\n"
    folder = args[0] if args else "INBOX"
    session.selected_folder = folder
    messages = await session.store.headers(session.username, folder)
    exists = len(messages)
    session.state = "SELECTED"
    return f"* {exists} EXISTS\r\n{tag} OK [READ-WRITE] SELECT completed\r\n"
