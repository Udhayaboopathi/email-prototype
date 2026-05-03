from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db
from core.security import decode_token
from models.login_activity import LoginActivity
from sqlalchemy import desc, select
from schemas.auth import ForgotPasswordRequest, LoginRequest, LoginResponse, ResetPasswordRequest, TokenPair, TokenRefreshRequest
from schemas.user import UserResponse
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db), x_forwarded_for: str | None = Header(default=None), user_agent: str | None = Header(default=None)):
    service = AuthService(db)
    return await service.login(payload.email, payload.password, x_forwarded_for or "127.0.0.1", user_agent or "api", payload.totp_code)


@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: TokenRefreshRequest, db: AsyncSession = Depends(get_db)):
    token_payload = decode_token(payload.refresh_token)
    if token_payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    service = AuthService(db)
    return await service.refresh(token_payload["sub"], payload.refresh_token)


@router.post("/forgot-password", response_model=dict[str, str])
async def forgot_password(payload: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    token = await AuthService(db).create_password_reset(payload.email)
    return {"reset_token": token}


@router.post("/reset-password", response_model=dict[str, bool])
async def reset_password(payload: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    ok = await AuthService(db).reset_password(payload.token, payload.new_password)
    return {"success": ok}


@router.post("/totp/setup", response_model=dict[str, str])
async def setup_totp(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    secret = await AuthService(db).enable_totp(user.id)
    return {"secret": secret}


@router.post("/totp/verify", response_model=dict[str, bool])
async def verify_totp(payload: dict[str, str], user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    code = payload.get("code", "")
    return {"verified": await AuthService(db).verify_totp(user.id, code)}


@router.get("/me", response_model=UserResponse)
async def me(user=Depends(get_current_user)):
    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role.value,
        domain_id=user.domain_id,
        is_active=user.is_active,
        totp_enabled=user.totp_enabled,
        created_at=user.created_at,
    )


@router.get("/login-activity", response_model=list[dict[str, str | None]])
async def login_activity(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    rows = list(
        await db.scalars(
            select(LoginActivity).where(LoginActivity.user_id == user.id).order_by(desc(LoginActivity.created_at)).limit(50)
        )
    )
    return [
        {
            "id": row.id,
            "ip_address": row.ip_address,
            "location": getattr(row, "country", None),
        }
        for row in rows
    ]
