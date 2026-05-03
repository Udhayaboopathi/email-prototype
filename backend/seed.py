import asyncio

from sqlalchemy import select

from config import get_settings
from core.security import hash_password
from database import SessionLocal
from models.user import User, UserRole


async def seed() -> None:
    settings = get_settings()
    async with SessionLocal() as session:
        existing = await session.scalar(select(User).where(User.email == settings.super_admin_email))
        if not existing:
            user = User(
                email=settings.super_admin_email,
                password_hash=hash_password(settings.super_admin_password),
                role=UserRole.super_admin,
                is_active=True,
            )
            session.add(user)
            await session.commit()

    print(f"Super admin created. Login at {settings.frontend_url}/login")
    print("1. Add your first domain in the super admin panel")
    print("2. Configure DNS records or enter Cloudflare token")
    print("3. Assign a domain admin")
    print("4. Create mailboxes")


if __name__ == "__main__":
    asyncio.run(seed())
