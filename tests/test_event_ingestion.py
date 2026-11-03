"""
Test suite validating event tracking, deduplication, and budget deduction.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_impression_and_click_tracking(client: AsyncClient):
    # Track Impression
    imp_req = {
        "event_id": "evt_imp_001",
        "event_type": "IMPRESSION",
        "campaign_id": "cmp_fintech_01",
        "publisher_id": "pub_live",
        "user_id": "usr_test_123",
        "clearing_price_cpm": 3.50
    }
    resp1 = await client.post("/api/v1/events/track", json=imp_req)
    assert resp1.status_code == 200
    d1 = resp1.json()
    assert d1["status"] == "RECORDED"
    assert d1["deduplicated"] is False

    # Track Click
    clk_req = {
        "event_id": "evt_clk_001",
        "event_type": "CLICK",
        "campaign_id": "cmp_fintech_01",
        "publisher_id": "pub_live",
        "user_id": "usr_test_123"
    }
    resp2 = await client.post("/api/v1/events/track", json=clk_req)
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "RECORDED"


@pytest.mark.asyncio
async def test_event_deduplication(client: AsyncClient):
    event_payload = {
        "event_id": "evt_unique_100",
        "event_type": "CLICK",
        "campaign_id": "cmp_ecommerce_02",
        "publisher_id": "pub_shop",
        "user_id": "usr_dedup_user"
    }

    # First send -> RECORDED
    resp1 = await client.post("/api/v1/events/track", json=event_payload)
    assert resp1.status_code == 200
    assert resp1.json()["deduplicated"] is False

    # Second send with same ID and payload -> DUPLICATE_IGNORED
    resp2 = await client.post("/api/v1/events/track", json=event_payload)
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "DUPLICATE_IGNORED"
    assert resp2.json()["deduplicated"] is True
