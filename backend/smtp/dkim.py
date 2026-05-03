from pathlib import Path

import dkim

from config import get_settings


def sign_message(raw_message: bytes, domain: str) -> bytes:
    settings = get_settings()
    private_key_path = Path("infra/dkim/keys") / domain / f"{settings.dkim_selector}.private"
    if not private_key_path.exists():
        return raw_message
    private_key = private_key_path.read_bytes()
    signature = dkim.sign(
        raw_message,
        selector=settings.dkim_selector.encode("utf-8"),
        domain=domain.encode("utf-8"),
        privkey=private_key,
        include_headers=[b"from", b"to", b"subject", b"date", b"message-id"],
    )
    return signature + raw_message
