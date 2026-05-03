import base64
import hashlib

from cryptography.fernet import Fernet

from config import get_settings


def _derive_key(secret: str) -> bytes:
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


def _cipher() -> Fernet:
    settings = get_settings()
    return Fernet(_derive_key(settings.encryption_secret_key))


def encrypt_value(plain_text: str) -> str:
    return _cipher().encrypt(plain_text.encode("utf-8")).decode("utf-8")


def decrypt_value(cipher_text: str) -> str:
    return _cipher().decrypt(cipher_text.encode("utf-8")).decode("utf-8")
