from dataclasses import dataclass, field

from sqlalchemy import select

from core.security import verify_password
from database import SessionLocal
from imap.commands import COMMAND_HANDLERS
from imap.maildir import MaildirStore
from models.user import User


@dataclass
class IMAPSession:
    reader: object
    writer: object
    state: str = "NOT_AUTHENTICATED"
    username: str = ""
    selected_folder: str = "INBOX"
    store: MaildirStore = field(default_factory=MaildirStore)

    async def authenticate(self, username: str, password: str) -> bool:
        async with SessionLocal() as db:
            user = await db.scalar(select(User).where(User.email == username))
            if not user:
                return False
            hashed = getattr(user, "hashed_password", None) or getattr(user, "password_hash", None)
            if not hashed:
                return False
            if not verify_password(password, hashed):
                return False
            self.username = username
            return True

    async def handle_line(self, line: str) -> str:
        parts = line.strip().split()
        if len(parts) < 2:
            return "* BAD Invalid command\r\n"

        tag, command, *args = parts
        command = command.upper()

        if command == "LOGOUT":
            self.state = "LOGOUT"
            return "* BYE LOGOUT requested\r\n" + f"{tag} OK LOGOUT completed\r\n"

        if command == "NOOP":
            return f"{tag} OK NOOP completed\r\n"

        handler = COMMAND_HANDLERS.get(command)
        if not handler:
            return f"{tag} BAD Unsupported command\r\n"

        if self.state == "NOT_AUTHENTICATED" and command not in {"LOGIN"}:
            return f"{tag} NO Authenticate first\r\n"

        response = await handler(self, tag, args)
        if command == "LOGIN" and " OK " in response:
            self.state = "AUTHENTICATED"
        elif command in {"SELECT", "EXAMINE"} and " OK " in response:
            self.state = "SELECTED"
        return response

    async def run(self) -> None:
        self.writer.write(b"* OK IMAP4rev1 Service Ready\r\n")
        await self.writer.drain()

        while True:
            line = await self.reader.readline()
            if not line:
                break

            # Pipelining support: process each complete line in order without waiting for extra reads.
            response = await self.handle_line(line.decode("utf-8", errors="ignore"))
            self.writer.write(response.encode("utf-8"))
            await self.writer.drain()

            if self.state == "LOGOUT":
                break

        self.writer.close()
        await self.writer.wait_closed()
