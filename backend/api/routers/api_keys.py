import hashlib
import secrets

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db
from models.api_key import APIKey
from schemas.api_key import APIKeyCreate, APIKeyResponse

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.post("/", response_model=dict[str, str | APIKeyResponse])
async def create_api_key(payload: APIKeyCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    plaintext = f"ms_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(plaintext.encode("utf-8")).hexdigest()
    row = APIKey(user_id=user.id, name=payload.name, key_hash=key_hash, is_active=True)
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return {
        "api_key": plaintext,
        "meta": APIKeyResponse(id=row.id, user_id=row.user_id, name=row.name, is_active=row.is_active, created_at=row.created_at).model_dump_json(),
    }


@router.get("/", response_model=list[APIKeyResponse])
async def list_api_keys(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    rows = await db.scalars(select(APIKey).where(APIKey.user_id == user.id))
    return [APIKeyResponse(id=r.id, user_id=r.user_id, name=r.name, is_active=r.is_active, created_at=r.created_at) for r in rows]
