"""
Real-time ad decisioning endpoint.
"""
from fastapi import APIRouter, status
from app.models.ad_request import AdDecisionRequest, AdDecisionResponse
from app.services.decisioning_engine import decisioning_engine

router = APIRouter(prefix="/ad", tags=["Real-Time Ad Decisioning"])


@router.post("/decision", response_model=AdDecisionResponse, status_code=status.HTTP_200_OK)
def request_ad_decision(request: AdDecisionRequest):
    """
    Evaluates real-time ad serving decisioning within sub-15ms.
    Validates targeting, frequency capping, budget availability, and resolves highest eCPM bid.
    """
    return decisioning_engine.evaluate_request(request)
