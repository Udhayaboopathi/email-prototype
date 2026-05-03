from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db
from services.pgp_service import PGPService

router = APIRouter(prefix="/pgp", tags=["pgp"])


@router.post("/keys", response_model=dict[str, str])
async def save_keys(payload: dict[str, str], db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    key = await PGPService(db).save_keypair(user.id, payload["public_key"], payload["private_key"])
    return {"fingerprint": key.fingerprint}
