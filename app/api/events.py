"""
High-throughput event tracking endpoint for impressions, clicks, and conversions.
"""
from fastapi import APIRouter, status
from app.models.event import TrackEventRequest, TrackEventResponse
from app.services.event_ingestion_service import event_ingestion_service

router = APIRouter(prefix="/events", tags=["Event Ingestion & Deduplication"])


@router.post("/track", response_model=TrackEventResponse, status_code=status.HTTP_200_OK)
def track_event(event: TrackEventRequest):
    """
    Ingests impression, click, or conversion events with atomic SHA-256 deduplication
    and real-time budget pacing deduction.
    """
    return event_ingestion_service.ingest_event(event)
