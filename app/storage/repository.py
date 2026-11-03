"""
Thread-safe repository simulating high-speed persistence and analytics tables.
"""
import threading
import uuid
from typing import Dict, List, Optional
from datetime import datetime

from app.models.campaign import Campaign, CampaignCreate, CampaignStatus
from app.models.event import TrackEventRequest, EventType


class InMemoryAdTechRepository:
    def __init__(self):
        self._lock = threading.RLock()
        self._campaigns: Dict[str, Campaign] = {}
        self._events: List[TrackEventRequest] = []
        # user_id -> list of (event_type, campaign_id, timestamp, cost)
        self._user_journeys: Dict[str, List[Dict]] = {}
        
        self._seed_default_campaigns()

    def _seed_default_campaigns(self):
        c1 = Campaign(
            campaign_id="cmp_fintech_01",
            name="NeoBank High-Yield Savings",
            advertiser_id="adv_neobank",
            bid_cpm=4.50,
            total_budget=5000.0,
            daily_budget=500.0,
            spent=124.50,
            target_countries=["IN", "US", "SG"],
            target_devices=["MOBILE", "DESKTOP"],
            target_categories=["FINANCE", "TECH"],
            creative_url="https://cdn.adtech.io/creatives/neobank_300x250.png",
            frequency_cap_per_user=3,
            status=CampaignStatus.ACTIVE
        )
        c2 = Campaign(
            campaign_id="cmp_ecommerce_02",
            name="Festive Super Sale",
            advertiser_id="adv_shopfast",
            bid_cpm=2.80,
            total_budget=10000.0,
            daily_budget=1200.0,
            spent=840.0,
            target_countries=["IN"],
            target_devices=["MOBILE"],
            target_categories=["SHOPPING", "TECH", "LIFESTYLE"],
            creative_url="https://cdn.adtech.io/creatives/sale_banner_728x90.png",
            frequency_cap_per_user=5,
            status=CampaignStatus.ACTIVE
        )
        c3 = Campaign(
            campaign_id="cmp_saas_03",
            name="Cloud AI Workspace Pro",
            advertiser_id="adv_cloudai",
            bid_cpm=6.20,
            total_budget=8000.0,
            daily_budget=800.0,
            spent=7950.0,  # Nearly exhausted
            target_countries=["US", "GB", "DE"],
            target_devices=["DESKTOP"],
            target_categories=["TECH", "B2B"],
            creative_url="https://cdn.adtech.io/creatives/cloud_saas_leaderboard.png",
            frequency_cap_per_user=2,
            status=CampaignStatus.ACTIVE
        )
        self._campaigns[c1.campaign_id] = c1
        self._campaigns[c2.campaign_id] = c2
        self._campaigns[c3.campaign_id] = c3

    # --- Campaign CRUD ---
    def create_campaign(self, req: CampaignCreate) -> Campaign:
        with self._lock:
            cid = f"cmp_{uuid.uuid4().hex[:10]}"
            now = datetime.utcnow()
            campaign = Campaign(
                campaign_id=cid,
                spent=0.0,
                status=CampaignStatus.ACTIVE,
                created_at=now,
                updated_at=now,
                **req.model_dump()
            )
            self._campaigns[cid] = campaign
            return campaign

    def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        with self._lock:
            return self._campaigns.get(campaign_id)

    def list_campaigns(self, status: Optional[CampaignStatus] = None) -> List[Campaign]:
        with self._lock:
            camps = list(self._campaigns.values())
            if status:
                camps = [c for c in camps if c.status == status]
            return camps

    def update_campaign_status(self, campaign_id: str, new_status: CampaignStatus) -> Optional[Campaign]:
        with self._lock:
            camp = self._campaigns.get(campaign_id)
            if camp:
                camp.status = new_status
                camp.updated_at = datetime.utcnow()
            return camp

    def record_spend(self, campaign_id: str, amount: float):
        with self._lock:
            camp = self._campaigns.get(campaign_id)
            if camp:
                camp.spent += amount
                if camp.spent >= camp.total_budget:
                    camp.status = CampaignStatus.EXHAUSTED
                camp.updated_at = datetime.utcnow()

    # --- Events & Touchpoint Log ---
    def record_event(self, event: TrackEventRequest):
        with self._lock:
            self._events.append(event)
            # Record user touchpoint
            uid = event.user_id
            if uid not in self._user_journeys:
                self._user_journeys[uid] = []
            
            cost = (event.clearing_price_cpm / 1000.0) if event.event_type == EventType.IMPRESSION else 0.0
            self._user_journeys[uid].append({
                "event_type": event.event_type,
                "campaign_id": event.campaign_id,
                "timestamp": event.timestamp,
                "clearing_cost": cost,
                "conversion_value": event.conversion_value or 0.0
            })

    def get_events(self, campaign_id: Optional[str] = None) -> List[TrackEventRequest]:
        with self._lock:
            if campaign_id:
                return [e for e in self._events if e.campaign_id == campaign_id]
            return list(self._events)

    def get_user_journey(self, user_id: str) -> List[Dict]:
        with self._lock:
            return list(self._user_journeys.get(user_id, []))


    def reset(self):
        with self._lock:
            self._campaigns.clear()
            self._events.clear()
            self._user_journeys.clear()
            self._seed_default_campaigns()


repo = InMemoryAdTechRepository()
