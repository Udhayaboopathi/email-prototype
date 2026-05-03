import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import pyotp
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.ip_geo import ip_to_country
from core.security import create_access_token, create_refresh_token, hash_password, verify_password
from models.login_activity import LoginActivity
from models.password_reset_token import PasswordResetToken
from models.session import Session
from models.totp_secret import TOTPSecret
from models.user import User
from schemas.auth import LoginResponse, TokenPair


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    async def login(self, email: str, password: str, ip_address: str, user_agent: str, totp_code: str | None) -> LoginResponse:
        user = await self.db.scalar(select(User).where(User.email == email))
        if not user or not verify_password(password, user.password_hash):
            self.db.add(
                LoginActivity(
                    user_id=user.id if user else "00000000-0000-0000-0000-000000000000",
                    ip_address=ip_address,
                    country=await ip_to_country(ip_address),
                    user_agent=user_agent,
                    success=False,
                )
            )
            await self.db.commit()
            raise ValueError("Invalid credentials")

        totp = await self.db.scalar(select(TOTPSecret).where(TOTPSecret.user_id == user.id))
        if totp and totp.verified:
            if not totp_code or not pyotp.TOTP(totp.secret).verify(totp_code, valid_window=1):
                return LoginResponse(tokens=TokenPair(access_token="", refresh_token=""), requires_totp=True)

        access_token = create_access_token(user.id, str(user.role))
        refresh_token = create_refresh_token(user.id)
        session = Session(
            user_id=user.id,
            refresh_token_hash=self._hash_token(refresh_token),
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )
        self.db.add(session)
        self.db.add(
            LoginActivity(
                user_id=user.id,
                ip_address=ip_address,
                country=await ip_to_country(ip_address),
                user_agent=user_agent,
                success=True,
            )
        )
        await self.db.commit()
        return LoginResponse(tokens=TokenPair(access_token=access_token, refresh_token=refresh_token), requires_totp=False)

    async def refresh(self, user_id: str, refresh_token: str) -> TokenPair:
        session = await self.db.scalar(select(Session).where(Session.user_id == user_id, Session.refresh_token_hash == self._hash_token(refresh_token)))
        if not session:
            raise ValueError("Invalid refresh token")
        user = await self.db.get(User, user_id)
        role = str(user.role) if user else ""
        return TokenPair(access_token=create_access_token(user_id, role), refresh_token=create_refresh_token(user_id))

    async def enable_totp(self, user_id: str) -> str:
        secret = pyotp.random_base32()
        existing = await self.db.scalar(select(TOTPSecret).where(TOTPSecret.user_id == user_id))
        if existing:
            existing.secret = secret
            existing.verified = False
        else:
            self.db.add(TOTPSecret(user_id=user_id, secret=secret, verified=False))
        await self.db.commit()
        return secret

    async def verify_totp(self, user_id: str, code: str) -> bool:
        row = await self.db.scalar(select(TOTPSecret).where(TOTPSecret.user_id == user_id))
        if not row:
            return False
        valid = pyotp.TOTP(row.secret).verify(code, valid_window=1)
        if valid:
            row.verified = True
            user = await self.db.get(User, user_id)
            if user:
                user.totp_enabled = True
            await self.db.commit()
        return valid

    async def create_password_reset(self, email: str) -> str:
        user = await self.db.scalar(select(User).where(User.email == email))
        if not user:
            return ""
        token = secrets.token_urlsafe(48)
        self.db.add(
            PasswordResetToken(
                user_id=user.id,
                token=token,
                expires_at=datetime.now(UTC) + timedelta(hours=1),
                used=False,
            )
        )
        await self.db.commit()
        return token

    async def reset_password(self, token: str, new_password: str) -> bool:
        row = await self.db.scalar(select(PasswordResetToken).where(PasswordResetToken.token == token, PasswordResetToken.used.is_(False)))
        if not row or row.expires_at < datetime.now(UTC):
            return False
        user = await self.db.get(User, row.user_id)
        if not user:
            return False
        user.password_hash = hash_password(new_password)
        row.used = True
        await self.db.execute(delete(Session).where(Session.user_id == user.id))
        await self.db.commit()
        return True
