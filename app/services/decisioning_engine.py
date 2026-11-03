"""
Real-time Ad Decisioning Engine performing sub-15ms targeting, frequency capping, and auction clearing.
"""
import time
from typing import List, Optional

from app.models.ad_request import AdDecisionRequest, AdDecisionResponse, DecisionOutcome
from app.models.campaign import Campaign, CampaignStatus
from app.storage.repository import repo
from app.core.frequency_capper import frequency_capper


class DecisioningEngine:
    def __init__(self, repository=repo):
        self.repo = repository

    def evaluate_request(self, req: AdDecisionRequest) -> AdDecisionResponse:
        start_time = time.perf_counter()

        active_campaigns = self.repo.list_campaigns(status=CampaignStatus.ACTIVE)
        if not active_campaigns:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return AdDecisionResponse(
                decision=DecisionOutcome.NO_BID,
                request_id=req.request_id,
                decision_latency_ms=round(elapsed_ms, 2),
                rejection_reason="NO_ACTIVE_CAMPAIGNS"
            )

        eligible: List[Campaign] = []

        for camp in active_campaigns:
            # 1. Budget check
            if camp.spent >= camp.total_budget:
                continue

            # 2. Country Targeting
            if camp.target_countries and req.country.upper() not in [c.upper() for c in camp.target_countries]:
                continue

            # 3. Device Targeting
            if camp.target_devices and req.device_type.value not in [d.upper() for d in camp.target_devices]:
                continue

            # 4. Category Targeting
            if camp.target_categories and req.category.upper() not in [cat.upper() for cat in camp.target_categories]:
                continue

            # 5. Publisher Floor Price Check
            if camp.bid_cpm < req.floor_price_cpm:
                continue

            # 6. Frequency Capping via Redis-style in-memory slider
            if frequency_capper.is_capped(req.user_id, camp.campaign_id, camp.frequency_cap_per_user):
                continue

            eligible.append(camp)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        if not eligible:
            return AdDecisionResponse(
                decision=DecisionOutcome.NO_BID,
                request_id=req.request_id,
                decision_latency_ms=round(elapsed_ms, 2),
                rejection_reason="NO_ELIGIBLE_CAMPAIGN_MATCHED"
            )

        # Auction Ranking: Rank by highest bid_cpm (eCPM auction)
        eligible.sort(key=lambda c: c.bid_cpm, reverse=True)
        winner = eligible[0]

        # Clearing price: First price auction (or second price floor)
        clearing_price = winner.bid_cpm
        if len(eligible) > 1:
            second_price = eligible[1].bid_cpm + 0.01
            clearing_price = min(winner.bid_cpm, max(req.floor_price_cpm, second_price))

        # Record frequency cap impression for user
        frequency_capper.record_impression(req.user_id, winner.campaign_id)

        return AdDecisionResponse(
            decision=DecisionOutcome.SERVE,
            request_id=req.request_id,
            winning_campaign_id=winner.campaign_id,
            advertiser_id=winner.advertiser_id,
            creative_url=winner.creative_url,
            clearing_price_cpm=round(clearing_price, 2),
            decision_latency_ms=round(elapsed_ms, 2)
        )


decisioning_engine = DecisioningEngine()
