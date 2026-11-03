"""
Ad tracking event models for high-throughput ingestion.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    IMPRESSION = "IMPRESSION"
    CLICK = "CLICK"
    CONVERSION = "CONVERSION"


class TrackEventRequest(BaseModel):
    event_id: str = Field(..., description="Unique client event UUID")
    event_type: EventType
    campaign_id: str
    publisher_id: str
    user_id: str
    clearing_price_cpm: float = 0.0
    conversion_value: Optional[float] = Field(0.0, ge=0.0, description="Order / purchase value if CONVERSION")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TrackEventResponse(BaseModel):
    status: str
    event_id: str
    event_type: EventType
    deduplicated: bool = False
    message: str
