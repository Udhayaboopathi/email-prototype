from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db
from schemas.campaign import CampaignCreate, CampaignResponse
from services.campaign_service import CampaignService

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post("/", response_model=CampaignResponse)
async def create_campaign(payload: CampaignCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    campaign = await CampaignService(db).create_campaign(user.id, payload.name, payload.subject, payload.body_html, payload.scheduled_at)
    return CampaignResponse(
        id=campaign.id,
        user_id=campaign.user_id,
        name=campaign.name,
        subject=campaign.subject,
        body_html=campaign.body_html,
        status=campaign.status,
        scheduled_at=campaign.scheduled_at,
        sent_at=campaign.sent_at,
    )


@router.get("/", response_model=list[CampaignResponse])
async def list_campaigns(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    rows = await CampaignService(db).list_campaigns(user.id)
    return [
        CampaignResponse(
            id=row.id,
            user_id=row.user_id,
            name=row.name,
            subject=row.subject,
            body_html=row.body_html,
            status=row.status,
            scheduled_at=row.scheduled_at,
            sent_at=row.sent_at,
        )
        for row in rows
    ]
