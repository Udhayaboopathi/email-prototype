import hashlib
import secrets
import hmac

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db
from models.webhook import Webhook
from schemas.webhook import WebhookCreate, WebhookResponse

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/", response_model=WebhookResponse)
async def create_webhook(payload: WebhookCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    secret = payload.secret or secrets.token_urlsafe(32)
    row = Webhook(user_id=user.id, url=payload.url, secret=secret, event_types=payload.event_types, is_active=True)
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return WebhookResponse(id=row.id, user_id=row.user_id, url=row.url, event_types=row.event_types, is_active=row.is_active, created_at=row.created_at)


@router.get("/", response_model=list[WebhookResponse])
async def list_webhooks(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    rows = await db.scalars(select(Webhook).where(Webhook.user_id == user.id))
    return [WebhookResponse(id=r.id, user_id=r.user_id, url=r.url, event_types=r.event_types, is_active=r.is_active, created_at=r.created_at) for r in rows]


@router.post("/dispatch/{webhook_id}", response_model=dict[str, str])
async def dispatch(webhook_id: str, payload: dict[str, str], db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    hook = await db.scalar(select(Webhook).where(Webhook.id == webhook_id, Webhook.user_id == user.id))
    if not hook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    body = payload.get("body", "{}").encode("utf-8")
    signature = hmac.new(hook.secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(hook.url, content=body, headers={"X-Webhook-Signature": signature, "Content-Type": "application/json"})
    return {"status": "sent"}
