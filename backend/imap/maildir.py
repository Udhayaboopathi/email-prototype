import asyncio
from email import message_from_bytes, policy
from pathlib import Path

from config import get_settings


class MaildirStore:
    def __init__(self) -> None:
        settings = get_settings()
        self.base = Path(settings.maildir_base)

    def _mailbox_folder(self, mailbox: str, folder: str) -> Path:
        safe_mailbox = mailbox.replace("@", "_at_")
        return self.base / safe_mailbox / folder

    async def list_messages(self, mailbox: str, folder: str = "INBOX") -> list[tuple[str, bytes]]:
        folder_path = self._mailbox_folder(mailbox, folder) / "cur"
        if not folder_path.exists():
            return []

        def _read() -> list[tuple[str, bytes]]:
            rows: list[tuple[str, bytes]] = []
            for path in folder_path.glob("*"):
                rows.append((path.name, path.read_bytes()))
            return sorted(rows, key=lambda x: x[0])

        return await asyncio.to_thread(_read)

    async def append_message(self, mailbox: str, folder: str, raw: bytes, uid: str) -> None:
        folder_path = self._mailbox_folder(mailbox, folder) / "cur"
        folder_path.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread((folder_path / uid).write_bytes, raw)

    async def headers(self, mailbox: str, folder: str = "INBOX") -> list[dict[str, str]]:
        data = await self.list_messages(mailbox, folder)
        result: list[dict[str, str]] = []
        for uid, raw in data:
            msg = message_from_bytes(raw, policy=policy.default)
            result.append({"uid": uid, "subject": msg.get("subject", ""), "from": msg.get("from", ""), "date": msg.get("date", "")})
        return result
