"""
Autonomous AI Agent endpoints for campaign decisioning and bid optimization.
"""
from fastapi import APIRouter, Query, status
from app.services.ai_optimization_agent import ai_optimization_agent, OptimizationReport

router = APIRouter(prefix="/ai", tags=["Autonomous AI Optimization Agent"])


@router.post("/optimize-campaigns", response_model=OptimizationReport, status_code=status.HTTP_200_OK)
def run_autonomous_optimization(auto_apply: bool = Query(False, description="Automatically adjust live bids and budgets")):
    """
    Triggers autonomous AI agent evaluation across active campaigns.
    Calculates bid adjustments, creative fatigue alerts, and pacing optimizations based on ROAS performance.
    """
    return ai_optimization_agent.optimize_campaigns(auto_apply=auto_apply)
