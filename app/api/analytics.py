"""
ROAS and Multi-Touch Attribution analytics endpoints.
"""
from fastapi import APIRouter, Query
from typing import Optional

from app.models.attribution import (
    AttributionModel,
    PlatformAttributionSummary
)
from app.services.attribution_service import attribution_service

router = APIRouter(prefix="/analytics", tags=["ROAS & Multi-Touch Attribution"])


@router.get("/roas", response_model=PlatformAttributionSummary)
def get_roas_report(
    campaign_id: Optional[str] = Query(None, description="Optional campaign filter"),
    model: AttributionModel = Query(AttributionModel.LAST_TOUCH, description="Attribution methodology")
):
    """
    Computes real-time ROAS, CTR, CVR, total spend, and attributed conversion values
    across campaigns using the specified attribution model.
    """
    return attribution_service.calculate_campaign_roas(campaign_id=campaign_id, model=model)
