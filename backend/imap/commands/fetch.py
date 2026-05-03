from __future__ import annotations

from email import message_from_bytes, policy
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from imap.session import IMAPSession



async def handle(session: IMAPSession, tag: str, args: list[str]) -> str:
    if session.state != "SELECTED":
        return f"{tag} NO SELECT mailbox first\r\n"
    headers = await session.store.list_messages(session.username, session.selected_folder)
    output = []
    for idx, (_, raw) in enumerate(headers, start=1):
        msg = message_from_bytes(raw, policy=policy.default)
        subject = msg.get("subject", "")
        output.append(f'* {idx} FETCH (BODY[HEADER.FIELDS (SUBJECT)] {{0}}\r\nSubject: {subject}\r\n)\r\n')
    return "".join(output) + f"{tag} OK FETCH completed\r\n"
