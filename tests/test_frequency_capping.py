"""
Test suite validating sliding window frequency capping per user and campaign.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_frequency_capping_enforcement(client: AsyncClient):
    user_id = "user_freq_test_1"
    # Campaign 'cmp_fintech_01' has frequency_cap_per_user = 3
    req = {
        "request_id": "req_freq_1",
        "publisher_id": "pub_live",
        "user_id": user_id,
        "device_type": "MOBILE",
        "country": "IN",
        "category": "FINANCE",
        "floor_price_cpm": 1.00
    }

    # First 3 impressions should serve cmp_fintech_01
    for i in range(3):
        req["request_id"] = f"req_freq_{i}"
        resp = await client.post("/api/v1/ad/decision", json=req)
        assert resp.status_code == 200
        assert resp.json()["decision"] == "SERVE"
        assert resp.json()["winning_campaign_id"] == "cmp_fintech_01"

    # 4th request: cmp_fintech_01 is frequency capped!
    # No other campaign targets (IN + MOBILE + FINANCE), so NO_BID
    req["request_id"] = "req_freq_4"
    resp4 = await client.post("/api/v1/ad/decision", json=req)
    assert resp4.status_code == 200
    assert resp4.json()["decision"] == "NO_BID"
    assert resp4.json()["rejection_reason"] == "NO_ELIGIBLE_CAMPAIGN_MATCHED"
