import logging
import ssl
from pathlib import Path

from aiosmtpd.controller import Controller
from aiosmtpd.smtp import AuthResult, LoginPassword, SMTP

from config import get_settings
from smtp.handler import InboundSMTPHandler

logger = logging.getLogger(__name__)

_CERT_PATHS = [
    ("/etc/ssl/mail/fullchain.pem", "/etc/ssl/mail/privkey.pem"),
    ("/etc/ssl/mail.crt", "/etc/ssl/mail.key"),
]


async def _auth_callback(server: SMTP, session, envelope, mechanism: str, auth_data) -> AuthResult:  # type: ignore[no-untyped-def]
    if mechanism != "LOGIN" or not isinstance(auth_data, LoginPassword):
        return AuthResult(success=False, handled=False)
    settings = get_settings()
    username = auth_data.login.decode("utf-8", errors="ignore")
    password = auth_data.password.decode("utf-8", errors="ignore")
    ok = await InboundSMTPHandler().verify_submission_auth(username, password, settings)
    return AuthResult(success=ok, handled=True)


def _tls_context() -> ssl.SSLContext | None:
    """Return an SSLContext if certificates exist, otherwise None."""
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    for cert_path, key_path in _CERT_PATHS:
        if Path(cert_path).exists() and Path(key_path).exists():
            try:
                context.load_cert_chain(cert_path, key_path)
                context.minimum_version = ssl.TLSVersion.TLSv1_2
                logger.info("SMTP TLS enabled using %s", cert_path)
                return context
            except Exception as exc:
                logger.warning("Failed to load cert %s: %s", cert_path, exc)

    logger.warning(
        "No TLS certificates found at %s. "
        "SMTP will start without TLS. "
        "Generate certs and mount them at /etc/ssl/mail/ to enable TLS.",
        [p[0] for p in _CERT_PATHS],
    )
    return None


async def create_smtp_servers() -> tuple[Controller, Controller]:
    tls_ctx = _tls_context()
    handler = InboundSMTPHandler()

    # Port 25 — inbound relay, TLS optional (STARTTLS opportunistic)
    smtp25_kwargs: dict = {
        "hostname": "0.0.0.0",
        "port": 25,
        "require_starttls": False,
    }
    if tls_ctx:
        smtp25_kwargs["tls_context"] = tls_ctx

    smtp25 = Controller(handler, **smtp25_kwargs)

    # Port 587 — submission, prefer TLS but fall back gracefully
    smtp587_kwargs: dict = {
        "hostname": "0.0.0.0",
        "port": 587,
        "require_starttls": tls_ctx is not None,
        "auth_required": True,
        "auth_require_tls": tls_ctx is not None,
        "authenticator": _auth_callback,
    }
    if tls_ctx:
        smtp587_kwargs["tls_context"] = tls_ctx

    smtp587 = Controller(handler, **smtp587_kwargs)

    smtp25.start()
    smtp587.start()
    return smtp25, smtp587
