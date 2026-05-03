"""
Email notification service — sends system emails (invites, password resets, etc.)
using the platform's own SMTP outbound stack.
"""
from __future__ import annotations

import asyncio
import logging

from config import get_settings
from smtp.outbound import send_direct

logger = logging.getLogger(__name__)


# ─── HTML template helpers ────────────────────────────────────────────────────

def _base_html(title: str, body: str) -> str:
    settings = get_settings()
    hostname = settings.smtp_hostname
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;background:#f4f6f8;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f8;padding:40px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
        <!-- Header -->
        <tr>
          <td style="background:linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);padding:32px 40px;">
            <h1 style="margin:0;color:#ffffff;font-size:24px;font-weight:700;letter-spacing:-0.5px;">
              ✉️ {hostname}
            </h1>
            <p style="margin:4px 0 0;color:rgba(255,255,255,0.6);font-size:13px;">
              Secure Mail Platform
            </p>
          </td>
        </tr>
        <!-- Body -->
        <tr>
          <td style="padding:40px;">
            {body}
          </td>
        </tr>
        <!-- Footer -->
        <tr>
          <td style="background:#f8f9fa;padding:24px 40px;border-top:1px solid #e9ecef;">
            <p style="margin:0;color:#6c757d;font-size:12px;text-align:center;">
              This email was sent by {hostname}. If you did not expect this, you can safely ignore it.
            </p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


# ─── Send domain admin invitation ─────────────────────────────────────────────

async def send_domain_admin_invite(
    *,
    to_email: str,
    domain_name: str,
    invite_token: str,
    invited_by_email: str,
) -> bool:
    """
    Send a domain-admin invitation email.
    Returns True if delivered, False on failure.
    """
    settings = get_settings()
    from_address = f"noreply@{settings.smtp_hostname}"
    invite_url = f"{settings.invite_base_url}/invite/{invite_token}"

    subject = f"You've been invited to manage {domain_name} on {settings.smtp_hostname}"

    text_body = f"""Hello,

You have been invited by {invited_by_email} to become the administrator of {domain_name} on {settings.smtp_hostname}.

To accept this invitation and set up your account, click the link below:

{invite_url}

This invitation link expires in 48 hours.

If you did not expect this invitation, you can safely ignore this email.

— The {settings.smtp_hostname} Team
"""

    html_body_content = f"""
<h2 style="margin:0 0 8px;color:#1a1a2e;font-size:22px;">You're invited! 🎉</h2>
<p style="margin:0 0 24px;color:#495057;font-size:15px;line-height:1.6;">
  <strong>{invited_by_email}</strong> has invited you to become the administrator of
  <strong style="color:#1a1a2e;">{domain_name}</strong> on this mail platform.
</p>

<table cellpadding="0" cellspacing="0" style="margin:0 0 24px;">
  <tr>
    <td style="background:#f8f9fa;border-radius:6px;padding:16px 20px;border-left:4px solid #4f46e5;">
      <p style="margin:0;color:#495057;font-size:13px;">Your domain admin account will be created for:</p>
      <p style="margin:4px 0 0;color:#1a1a2e;font-size:16px;font-weight:600;">{to_email}</p>
    </td>
  </tr>
</table>

<p style="margin:0 0 24px;color:#495057;font-size:15px;line-height:1.6;">
  Click the button below to accept the invitation and set your password:
</p>

<table cellpadding="0" cellspacing="0" style="margin:0 0 32px;">
  <tr>
    <td style="background:linear-gradient(135deg,#4f46e5,#7c3aed);border-radius:6px;padding:14px 28px;">
      <a href="{invite_url}"
         style="color:#ffffff;text-decoration:none;font-size:15px;font-weight:600;display:block;">
        Accept Invitation &rarr;
      </a>
    </td>
  </tr>
</table>

<p style="margin:0 0 8px;color:#6c757d;font-size:13px;">
  Or copy and paste this link into your browser:
</p>
<p style="margin:0;word-break:break-all;">
  <a href="{invite_url}" style="color:#4f46e5;font-size:12px;font-family:monospace;">{invite_url}</a>
</p>

<hr style="margin:32px 0;border:none;border-top:1px solid #e9ecef;"/>
<p style="margin:0;color:#6c757d;font-size:13px;">
  ⏰ This invitation link expires in <strong>48 hours</strong>.<br/>
  If you did not expect this invitation, you can safely ignore this email.
</p>
"""

    html_body = _base_html(subject, html_body_content)

    try:
        result = await send_direct(
            from_address=from_address,
            to_addresses=[to_email],
            subject=subject,
            body_text=text_body,
            body_html=html_body,
        )
        if not result["success"]:
            logger.warning(
                "Invite email delivery failed for %s: failed_recipients=%s",
                to_email,
                result.get("failed_recipients"),
            )
            return False
        logger.info("Invite email sent to %s for domain %s", to_email, domain_name)
        return True
    except Exception as exc:
        logger.error("Failed to send invite email to %s: %s", to_email, exc)
        return False


# ─── Send password reset ───────────────────────────────────────────────────────

async def send_password_reset(*, to_email: str, reset_token: str) -> bool:
    """Send a password-reset link email."""
    settings = get_settings()
    from_address = f"noreply@{settings.smtp_hostname}"
    reset_url = f"{settings.frontend_url}/reset-password?token={reset_token}"

    subject = f"Reset your {settings.smtp_hostname} password"

    text_body = f"""Hello,

We received a request to reset the password for your account ({to_email}).

Click the link below to choose a new password:
{reset_url}

This link expires in 1 hour. If you did not request a password reset, ignore this email.

— The {settings.smtp_hostname} Team
"""

    html_body_content = f"""
<h2 style="margin:0 0 16px;color:#1a1a2e;font-size:22px;">Reset your password</h2>
<p style="margin:0 0 24px;color:#495057;font-size:15px;line-height:1.6;">
  We received a request to reset the password for <strong>{to_email}</strong>.
  Click the button below to choose a new password.
</p>
<table cellpadding="0" cellspacing="0" style="margin:0 0 32px;">
  <tr>
    <td style="background:#dc3545;border-radius:6px;padding:14px 28px;">
      <a href="{reset_url}"
         style="color:#ffffff;text-decoration:none;font-size:15px;font-weight:600;display:block;">
        Reset Password &rarr;
      </a>
    </td>
  </tr>
</table>
<p style="margin:0;color:#6c757d;font-size:13px;">
  ⏰ This link expires in <strong>1 hour</strong>.<br/>
  If you did not request this, ignore this email — your password will not change.
</p>
"""

    try:
        result = await send_direct(
            from_address=from_address,
            to_addresses=[to_email],
            subject=subject,
            body_text=text_body,
            body_html=html_body_content,
        )
        return result["success"]
    except Exception as exc:
        logger.error("Failed to send password reset email to %s: %s", to_email, exc)
        return False
