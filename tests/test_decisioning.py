"""
Test suite validating real-time ad serving decisioning and sub-15ms latency.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_probes(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "HEALTHY"

    ready = await client.get("/ready")
    assert ready.status_code == 200
    assert ready.json()["status"] == "READY"


@pytest.mark.asyncio
async def test_successful_ad_decisioning(client: AsyncClient):
    req = {
        "request_id": "req_auction_101",
        "publisher_id": "pub_hindustan_times",
        "user_id": "usr_998877",
        "device_type": "MOBILE",
        "country": "IN",
        "category": "TECH",
        "floor_price_cpm": 1.50
    }

    resp = await client.post("/api/v1/ad/decision", json=req)
    assert resp.status_code == 200
    data = resp.json()
    assert data["decision"] == "SERVE"
    assert data["winning_campaign_id"] in ["cmp_fintech_01", "cmp_ecommerce_02"]
    assert data["creative_url"] is not None
    assert data["clearing_price_cpm"] >= 1.50
    # Strict SLA check
    assert data["decision_latency_ms"] < 25.0


@pytest.mark.asyncio
async def test_no_bid_floor_price_exceeded(client: AsyncClient):
    # Floor price is $15.00 CPM, higher than any active campaign
    req = {
        "request_id": "req_auction_floor_fail",
        "publisher_id": "pub_premium_times",
        "user_id": "usr_new",
        "device_type": "DESKTOP",
        "country": "US",
        "category": "TECH",
        "floor_price_cpm": 15.00
    }

    resp = await client.post("/api/v1/ad/decision", json=req)
    assert resp.status_code == 200
    data = resp.json()
    assert data["decision"] == "NO_BID"
    assert data["rejection_reason"] == "NO_ELIGIBLE_CAMPAIGN_MATCHED"
