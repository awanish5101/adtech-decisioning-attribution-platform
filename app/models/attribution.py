"""
Attribution and ROAS (Return On Ad Spend) analytics models.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from enum import Enum


class AttributionModel(str, Enum):
    LAST_TOUCH = "LAST_TOUCH"
    FIRST_TOUCH = "FIRST_TOUCH"
    LINEAR = "LINEAR"


class CampaignROASReport(BaseModel):
    campaign_id: str
    campaign_name: str
    advertiser_id: str
    total_impressions: int
    total_clicks: int
    total_conversions: int
    click_through_rate: float     # CTR = (clicks / impressions) * 100
    conversion_rate: float         # CVR = (conversions / clicks) * 100
    total_ad_spend: float          # Spend from impressions/clicks
    total_conversion_revenue: float
    roas_multiplier: float         # ROAS = conversion_revenue / ad_spend
    attribution_model_used: AttributionModel


class PlatformAttributionSummary(BaseModel):
    total_campaigns: int
    total_events_processed: int
    overall_spend: float
    overall_revenue: float
    overall_platform_roas: float
    campaign_reports: List[CampaignROASReport]
