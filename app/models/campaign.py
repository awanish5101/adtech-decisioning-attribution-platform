"""
Campaign data models for the AdTech platform.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class CampaignStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    EXHAUSTED = "EXHAUSTED"


class CampaignCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    advertiser_id: str = Field(...)
    bid_cpm: float = Field(..., gt=0.0, description="Bid price per 1,000 impressions in USD")
    total_budget: float = Field(..., gt=0.0, description="Total budget in USD")
    daily_budget: float = Field(..., gt=0.0, description="Daily spend cap in USD")
    target_countries: List[str] = Field(default_factory=list, description="ISO country codes (e.g. ['US', 'IN'])")
    target_devices: List[str] = Field(default_factory=list, description="Device types (e.g. ['MOBILE', 'DESKTOP'])")
    target_categories: List[str] = Field(default_factory=list, description="IAB Categories (e.g. ['TECH', 'GAMING'])")
    creative_url: str = Field(..., description="CDN URL of the ad creative / banner")
    frequency_cap_per_user: int = Field(3, description="Max impressions per user per hour")


class Campaign(CampaignCreate):
    campaign_id: str
    spent: float = 0.0
    status: CampaignStatus = CampaignStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
