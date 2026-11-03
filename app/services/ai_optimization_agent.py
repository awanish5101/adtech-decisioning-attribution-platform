"""
Autonomous AI Agent for Campaign Optimization and Decisioning.
"""
from typing import List, Dict, Any
from pydantic import BaseModel

from app.services.attribution_service import attribution_service
from app.models.attribution import AttributionModel
from app.storage.repository import repo


class OptimizationAction(BaseModel):
    campaign_id: str
    campaign_name: str
    action_type: str  # "INCREASE_BID", "DECREASE_BID", "PAUSE_CAMPAIGN", "REFRESH_CREATIVE", "INCREASE_BUDGET"
    current_value: float
    recommended_value: float
    confidence_score: float
    reasoning: str


class OptimizationReport(BaseModel):
    total_campaigns_analyzed: int
    optimizations_recommended: int
    actions: List[OptimizationAction]


class AIOptimizationAgent:
    def __init__(self, repository=repo, attr_service=attribution_service):
        self.repo = repository
        self.attr_service = attr_service

    def optimize_campaigns(self, auto_apply: bool = False) -> OptimizationReport:
        summary = self.attr_service.calculate_campaign_roas(model=AttributionModel.LAST_TOUCH)
        actions: List[OptimizationAction] = []

        for report in summary.campaign_reports:
            camp = self.repo.get_campaign(report.campaign_id)
            if not camp:
                continue

            # Heuristic 1: High ROAS (> 3.0x) -> Scale up bid and budget
            if report.roas_multiplier >= 3.0:
                new_bid = round(camp.bid_cpm * 1.15, 2)
                actions.append(OptimizationAction(
                    campaign_id=camp.campaign_id,
                    campaign_name=camp.name,
                    action_type="INCREASE_BID",
                    current_value=camp.bid_cpm,
                    recommended_value=new_bid,
                    confidence_score=0.92,
                    reasoning=f"High ROAS of {report.roas_multiplier}x indicates strong conversion efficiency. Increase bid by 15% to win more ad auctions."
                ))
                if auto_apply:
                    camp.bid_cpm = new_bid

            # Heuristic 2: Negative ROAS (< 1.0x with spend > $10) -> Lower bid
            elif report.roas_multiplier < 1.0 and report.total_ad_spend > 10.0:
                new_bid = round(max(0.20, camp.bid_cpm * 0.80), 2)
                actions.append(OptimizationAction(
                    campaign_id=camp.campaign_id,
                    campaign_name=camp.name,
                    action_type="DECREASE_BID",
                    current_value=camp.bid_cpm,
                    recommended_value=new_bid,
                    confidence_score=0.88,
                    reasoning=f"Sub-optimal ROAS of {report.roas_multiplier}x indicates negative advertiser return. Lower bid by 20% to curb inefficient ad spend."
                ))
                if auto_apply:
                    camp.bid_cpm = new_bid

            # Heuristic 3: Creative Fatigue (CTR < 0.3% with impressions > 500)
            if report.total_impressions > 500 and report.click_through_rate < 0.3:
                actions.append(OptimizationAction(
                    campaign_id=camp.campaign_id,
                    campaign_name=camp.name,
                    action_type="REFRESH_CREATIVE",
                    current_value=report.click_through_rate,
                    recommended_value=1.5,
                    confidence_score=0.85,
                    reasoning=f"Low CTR ({report.click_through_rate}%) suggests creative fatigue. Recommend rotating banner ad assets."
                ))

        return OptimizationReport(
            total_campaigns_analyzed=len(summary.campaign_reports),
            optimizations_recommended=len(actions),
            actions=actions
        )


ai_optimization_agent = AIOptimizationAgent()
