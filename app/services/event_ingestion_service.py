"""
High-throughput event ingestion service with atomic deduplication and budget updates.
"""
from app.models.event import TrackEventRequest, TrackEventResponse, EventType
from app.storage.repository import repo
from app.core.deduplicator import deduplicator


class EventIngestionService:
    def __init__(self, repository=repo, dedup=deduplicator):
        self.repo = repository
        self.dedup = dedup

    def ingest_event(self, req: TrackEventRequest) -> TrackEventResponse:
        # Compute event deduplication hash
        event_hash = self.dedup.compute_hash(
            event_id=req.event_id,
            event_type=req.event_type.value,
            user_id=req.user_id,
            campaign_id=req.campaign_id
        )

        is_duplicate = self.dedup.check_and_set(event_hash)
        if is_duplicate:
            return TrackEventResponse(
                status="DUPLICATE_IGNORED",
                event_id=req.event_id,
                event_type=req.event_type,
                deduplicated=True,
                message="Event has already been processed. Deduplicated to prevent double billing."
            )

        # Record event in persistent ledger
        self.repo.record_event(req)

        # Update budget spend if impression
        if req.event_type == EventType.IMPRESSION and req.clearing_price_cpm > 0:
            spend_delta = req.clearing_price_cpm / 1000.0
            self.repo.record_spend(req.campaign_id, spend_delta)

        return TrackEventResponse(
            status="RECORDED",
            event_id=req.event_id,
            event_type=req.event_type,
            deduplicated=False,
            message="Event successfully ingested and recorded."
        )


event_ingestion_service = EventIngestionService()
