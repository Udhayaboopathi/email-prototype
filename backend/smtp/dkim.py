"""
DKIM key generation and signing utilities.

Each domain gets its own RSA-2048 key pair stored at:
  infra/dkim/keys/<domain>/<selector>.private
  infra/dkim/keys/<domain>/<selector>.public

The public key is also stored in Domain.dkim_public_key (DB) and pushed to
Cloudflare as a TXT record when dns_mode='auto'.
"""
from __future__ import annotations

import base64
from pathlib import Path

import dkim
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

from config import get_settings

# Base directory for DKIM key files (relative to the project root inside container)
DKIM_KEYS_BASE = Path("infra/dkim/keys")


# ─── Key generation ───────────────────────────────────────────────────────────

def generate_dkim_keypair(domain: str, selector: str | None = None) -> tuple[bytes, str, str]:
    """
    Generate a fresh RSA-2048 DKIM key pair for *domain*.

    Returns:
        private_key_pem  (bytes)  – PEM-encoded private key to store on disk
        public_key_b64   (str)    – base64 public key for the DNS TXT record value
        dns_txt_value    (str)    – full DKIM TXT record value ready to put in DNS
    """
    settings = get_settings()
    sel = selector or settings.dkim_selector

    # Generate RSA key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend(),
    )

    # Private key in PKCS8 PEM (what the dkim library expects)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # Public key in SubjectPublicKeyInfo DER, then base64 (no line breaks)
    pub_der = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    pub_b64 = base64.b64encode(pub_der).decode("ascii")

    # DNS TXT record value
    dns_txt = f"v=DKIM1; k=rsa; p={pub_b64}"

    return private_pem, pub_b64, dns_txt


def save_dkim_private_key(domain: str, private_pem: bytes, selector: str | None = None) -> Path:
    """
    Write the private key PEM to disk at infra/dkim/keys/<domain>/<selector>.private
    Creates directories as needed.
    Returns the path written.
    """
    settings = get_settings()
    sel = selector or settings.dkim_selector
    key_dir = DKIM_KEYS_BASE / domain
    key_dir.mkdir(parents=True, exist_ok=True)
    key_path = key_dir / f"{sel}.private"
    key_path.write_bytes(private_pem)
    return key_path


def get_dkim_private_key(domain: str, selector: str | None = None) -> bytes | None:
    """
    Load the private key from disk for *domain*.
    Returns None if the key file doesn't exist.
    """
    settings = get_settings()
    sel = selector or settings.dkim_selector
    key_path = DKIM_KEYS_BASE / domain / f"{sel}.private"
    if not key_path.exists():
        return None
    return key_path.read_bytes()


# ─── Message signing ──────────────────────────────────────────────────────────

def sign_message(raw_message: bytes, domain: str) -> bytes:
    """
    Sign *raw_message* with the DKIM private key for *domain*.

    Falls back gracefully (returns unsigned message) if:
    - No key file exists for the domain
    - The dkim library raises any error
    """
    settings = get_settings()
    selector = settings.dkim_selector

    private_key = get_dkim_private_key(domain, selector)
    if private_key is None:
        # No per-domain key — return unsigned (recipient will see no DKIM signature)
        return raw_message

    try:
        signature = dkim.sign(
            raw_message,
            selector=selector.encode("utf-8"),
            domain=domain.encode("utf-8"),
            privkey=private_key,
            include_headers=[b"from", b"to", b"subject", b"date", b"message-id"],
        )
        return signature + raw_message
    except Exception:
        # Signing failed — return unsigned rather than breaking delivery
        return raw_message
