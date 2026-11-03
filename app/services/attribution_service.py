"""
Attribution Modeling (Last-Touch, First-Touch, Linear) and ROAS Analytics Service.
"""
from typing import Dict, List, Optional
from collections import defaultdict

from app.models.attribution import (
    AttributionModel,
    CampaignROASReport,
    PlatformAttributionSummary
)
from app.models.event import EventType
from app.storage.repository import repo


class AttributionService:
    def __init__(self, repository=repo):
        self.repo = repository

    def calculate_campaign_roas(
        self,
        campaign_id: Optional[str] = None,
        model: AttributionModel = AttributionModel.LAST_TOUCH
    ) -> PlatformAttributionSummary:
        campaigns = self.repo.list_campaigns()
        if campaign_id:
            campaigns = [c for c in campaigns if c.campaign_id == campaign_id]

        all_events = self.repo.get_events()
        
        # Metrics aggregates per campaign
        impressions_count = defaultdict(int)
        clicks_count = defaultdict(int)
        conversions_count = defaultdict(int)
        spend_accumulated = defaultdict(float)
        revenue_attributed = defaultdict(float)

        # 1. Tally raw impressions, clicks, spend
        for evt in all_events:
            cid = evt.campaign_id
            if evt.event_type == EventType.IMPRESSION:
                impressions_count[cid] += 1
                spend_accumulated[cid] += (evt.clearing_price_cpm / 1000.0)
            elif evt.event_type == EventType.CLICK:
                clicks_count[cid] += 1

        # 2. Multi-touch attribution for conversions
        conversion_events = [e for e in all_events if e.event_type == EventType.CONVERSION]
        for conv in conversion_events:
            user_journey = self.repo.get_user_journey(conv.user_id)
            # Find touchpoints prior to conversion
            prior_touches = [
                t for t in user_journey
                if t["event_type"] in (EventType.IMPRESSION, EventType.CLICK) and t["timestamp"] <= conv.timestamp
            ]

            conv_value = conv.conversion_value or 0.0

            if not prior_touches:
                # Direct conversion attribution
                conversions_count[conv.campaign_id] += 1
                revenue_attributed[conv.campaign_id] += conv_value
            elif model == AttributionModel.LAST_TOUCH:
                last_touch = prior_touches[-1]
                target_cid = last_touch["campaign_id"]
                conversions_count[target_cid] += 1
                revenue_attributed[target_cid] += conv_value
            elif model == AttributionModel.FIRST_TOUCH:
                first_touch = prior_touches[0]
                target_cid = first_touch["campaign_id"]
                conversions_count[target_cid] += 1
                revenue_attributed[target_cid] += conv_value
            elif model == AttributionModel.LINEAR:
                weight = 1.0 / len(prior_touches)
                for touch in prior_touches:
                    t_cid = touch["campaign_id"]
                    conversions_count[t_cid] += weight
                    revenue_attributed[t_cid] += (conv_value * weight)

        # 3. Assemble reports
        reports: List[CampaignROASReport] = []
        total_spend = 0.0
        total_revenue = 0.0

        for camp in campaigns:
            cid = camp.campaign_id
            imps = impressions_count[cid]
            clks = clicks_count[cid]
            convs = int(round(conversions_count[cid]))
            raw_spend = spend_accumulated[cid] if spend_accumulated[cid] > 0 else camp.spent
            spend = round(raw_spend, 2) if raw_spend >= 0.01 else round(raw_spend, 4)
            rev = round(revenue_attributed[cid], 2)

            ctr = round((clks / imps * 100.0), 2) if imps > 0 else 0.0
            cvr = round((convs / clks * 100.0), 2) if clks > 0 else 0.0
            roas = round((rev / raw_spend), 2) if raw_spend > 0 else 0.0

            total_spend += spend
            total_revenue += rev

            reports.append(CampaignROASReport(
                campaign_id=cid,
                campaign_name=camp.name,
                advertiser_id=camp.advertiser_id,
                total_impressions=imps,
                total_clicks=clks,
                total_conversions=convs,
                click_through_rate=ctr,
                conversion_rate=cvr,
                total_ad_spend=spend,
                total_conversion_revenue=rev,
                roas_multiplier=roas,
                attribution_model_used=model
            ))

        platform_roas = round((total_revenue / total_spend), 2) if total_spend > 0 else 0.0

        return PlatformAttributionSummary(
            total_campaigns=len(reports),
            total_events_processed=len(all_events),
            overall_spend=round(total_spend, 2),
            overall_revenue=round(total_revenue, 2),
            overall_platform_roas=platform_roas,
            campaign_reports=reports
        )


attribution_service = AttributionService()
