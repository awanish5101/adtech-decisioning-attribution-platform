"""
Campaign management endpoints for the ad marketplace.
"""
from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional

from app.models.campaign import Campaign, CampaignCreate, CampaignStatus
from app.storage.repository import repo

router = APIRouter(prefix="/campaigns", tags=["Ad Marketplace Campaigns"])


@router.post("", response_model=Campaign, status_code=status.HTTP_201_CREATED)
def create_campaign(request: CampaignCreate):
    """Creates a new advertiser campaign in the marketplace."""
    return repo.create_campaign(request)


@router.get("", response_model=List[Campaign])
def list_campaigns(status_filter: Optional[CampaignStatus] = Query(None, alias="status")):
    """Lists campaigns with optional status filtering."""
    return repo.list_campaigns(status=status_filter)


@router.get("/{campaign_id}", response_model=Campaign)
def get_campaign(campaign_id: str):
    """Retrieves single campaign details and budget spend."""
    camp = repo.get_campaign(campaign_id)
    if not camp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Campaign '{campaign_id}' not found.")
    return camp


@router.patch("/{campaign_id}/status", response_model=Campaign)
def update_campaign_status(campaign_id: str, new_status: CampaignStatus):
    """Pauses or resumes campaign execution."""
    camp = repo.update_campaign_status(campaign_id, new_status)
    if not camp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Campaign '{campaign_id}' not found.")
    return camp
