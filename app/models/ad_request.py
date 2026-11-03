"""
Real-time ad decisioning request and response models.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum


class DeviceType(str, Enum):
    MOBILE = "MOBILE"
    DESKTOP = "DESKTOP"
    TABLET = "TABLET"
    CONNECTED_TV = "CONNECTED_TV"


class AdDecisionRequest(BaseModel):
    request_id: str = Field(..., description="Unique ad auction/request UUID")
    publisher_id: str = Field(..., description="Publishing app or website identifier")
    user_id: str = Field(..., description="Anonymized user identifier or cookie ID")
    device_type: DeviceType = Field(default=DeviceType.MOBILE)
    country: str = Field("IN", min_length=2, max_length=2, description="2-letter country code")
    category: str = Field("TECH", description="Placement category")
    floor_price_cpm: float = Field(0.50, ge=0.0, description="Minimum CPM floor price set by publisher")


class DecisionOutcome(str, Enum):
    SERVE = "SERVE"
    NO_BID = "NO_BID"


class AdDecisionResponse(BaseModel):
    decision: DecisionOutcome
    request_id: str
    winning_campaign_id: Optional[str] = None
    advertiser_id: Optional[str] = None
    creative_url: Optional[str] = None
    clearing_price_cpm: Optional[float] = None
    decision_latency_ms: float
    rejection_reason: Optional[str] = None
