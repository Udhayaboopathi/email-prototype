from collections.abc import AsyncGenerator

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import decode_token
from database import get_db_session
from models.user import User, UserRole
from models.domain import Domain


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db_session():
        yield session


async def get_current_user(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    user = await db.scalar(select(User).where(User.id == payload.get("sub"), User.is_active.is_(True)))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_role(*roles: UserRole):
    async def _inner(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return _inner


async def get_current_domain_admin(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Return the current domain admin user and attach the domain object to `user.domain`.
    Raises 401 for auth issues and 403 for non-domain-admin or suspended domains.
    """
    user = await get_current_user(authorization=authorization, db=db)
    if user.role != UserRole.domain_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    if not user.domain_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No domain assigned")
    domain = await db.get(Domain, user.domain_id)
    if not domain:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Domain not found")
    if getattr(domain, "is_suspended", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Domain suspended")
    # attach domain for downstream handlers
    setattr(user, "domain", domain)
    return user
