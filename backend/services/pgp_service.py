import hashlib

from core.encryption import encrypt_value
from models.pgp_key import PGPKey
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class PGPService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_keypair(self, user_id: str, public_key: str, private_key: str) -> PGPKey:
        fingerprint = hashlib.sha1(public_key.encode("utf-8")).hexdigest().upper()
        row = await self.db.scalar(select(PGPKey).where(PGPKey.user_id == user_id))
        if row:
            row.public_key = public_key
            row.private_key_encrypted = encrypt_value(private_key)
            row.fingerprint = fingerprint
        else:
            row = PGPKey(
                user_id=user_id,
                public_key=public_key,
                private_key_encrypted=encrypt_value(private_key),
                fingerprint=fingerprint,
            )
            self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return row
