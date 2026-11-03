"""
Test suite validating the Autonomous AI Campaign Optimization Agent.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_ai_optimization_agent_recommendations(client: AsyncClient):
    cid = "cmp_fintech_01"
    user = "usr_agent_test"

    # Seed impressions and a massive conversion to create high ROAS
    await client.post("/api/v1/events/track", json={
        "event_id": "imp_opt_1",
        "event_type": "IMPRESSION",
        "campaign_id": cid,
        "publisher_id": "pub_agent",
        "user_id": user,
        "clearing_price_cpm": 3.00
    })
    await client.post("/api/v1/events/track", json={
        "event_id": "conv_opt_1",
        "event_type": "CONVERSION",
        "campaign_id": cid,
        "publisher_id": "pub_agent",
        "user_id": user,
        "conversion_value": 500.00
    })

    # Trigger AI agent evaluation
    agent_resp = await client.post("/api/v1/ai/optimize-campaigns?auto_apply=false")
    assert agent_resp.status_code == 200
    data = agent_resp.json()
    assert data["total_campaigns_analyzed"] >= 1
    assert data["optimizations_recommended"] >= 1
    
    # Confirm recommendation type
    actions = [a["action_type"] for a in data["actions"]]
    assert "INCREASE_BID" in actions
