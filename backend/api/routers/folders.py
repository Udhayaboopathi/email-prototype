from fastapi import APIRouter, Depends

from api.deps import get_current_user

router = APIRouter(prefix="/folders", tags=["folders"])


@router.get("/", response_model=list[str])
async def list_folders(user=Depends(get_current_user)):
    return ["INBOX", "Sent", "Drafts", "Trash", "Spam", "Archive"]
