from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from imap.session import IMAPSession



async def handle(session: IMAPSession, tag: str, args: list[str]) -> str:
    if len(args) < 2:
        return f"{tag} BAD LOGIN requires username and password\r\n"
    username = args[0]
    password = args[1]
    if await session.authenticate(username, password):
        session.state = "AUTH"
        return f"{tag} OK LOGIN completed\r\n"
    return f"{tag} NO Authentication failed\r\n"
