from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from imap.session import IMAPSession


async def handle(session: IMAPSession, tag: str, args: list[str]) -> str:
    if session.state != "SELECTED":
        return f"{tag} NO SELECT mailbox first\r\n"
    query = " ".join(args).lower()
    rows = await session.store.headers(session.username, session.selected_folder)
    matched = [str(index + 1) for index, row in enumerate(rows) if query in row["subject"].lower() or query in row["from"].lower()]
    return f"* SEARCH {' '.join(matched)}\r\n{tag} OK SEARCH completed\r\n"
