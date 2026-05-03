from fastapi import APIRouter, Depends

from api.deps import get_current_user
from services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/summary", response_model=dict[str, str])
async def summary(payload: dict[str, str], user=Depends(get_current_user)):
    text = payload.get("text", "")
    return {"summary": await AIService().summarize_email(text)}


@router.post("/smart-reply", response_model=dict[str, str])
async def smart_reply(payload: dict[str, str], user=Depends(get_current_user)):
    text = payload.get("text", "")
    return {"reply": await AIService().smart_reply(text)}


@router.post("/priority", response_model=dict[str, int])
async def priority(payload: dict[str, str], user=Depends(get_current_user)):
    score = await AIService().priority_score(payload.get("subject", ""), payload.get("body", ""))
    return {"score": score}
