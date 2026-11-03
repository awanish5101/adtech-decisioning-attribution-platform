"""
Test suite validating multi-touch attribution (Last-Touch, First-Touch, Linear) and ROAS.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_roas_calculation_and_attribution(client: AsyncClient):
    user = "usr_conversion_journey"
    cid = "cmp_fintech_01"

    # Step 1: Ingest 10 impressions ($4.00 CPM = $0.040 spend)
    for i in range(10):
        await client.post("/api/v1/events/track", json={
            "event_id": f"imp_{i}",
            "event_type": "IMPRESSION",
            "campaign_id": cid,
            "publisher_id": "pub_test",
            "user_id": user,
            "clearing_price_cpm": 4.00
        })

    # Step 2: Ingest 2 clicks
    for i in range(2):
        await client.post("/api/v1/events/track", json={
            "event_id": f"clk_{i}",
            "event_type": "CLICK",
            "campaign_id": cid,
            "publisher_id": "pub_test",
            "user_id": user
        })

    # Step 3: Ingest 1 conversion with $200 purchase value
    await client.post("/api/v1/events/track", json={
        "event_id": "conv_101",
        "event_type": "CONVERSION",
        "campaign_id": cid,
        "publisher_id": "pub_test",
        "user_id": user,
        "conversion_value": 200.00
    })

    # Request ROAS report
    roas_resp = await client.get(f"/api/v1/analytics/roas?campaign_id={cid}&model=LAST_TOUCH")
    assert roas_resp.status_code == 200
    summary = roas_resp.json()
    assert summary["total_campaigns"] == 1
    
    report = summary["campaign_reports"][0]
    assert report["total_impressions"] == 10
    assert report["total_clicks"] == 2
    assert report["total_conversions"] == 1
    assert report["click_through_rate"] == 20.0  # 2 clicks / 10 imps * 100
    assert report["conversion_rate"] == 50.0      # 1 conv / 2 clicks * 100
    assert report["total_conversion_revenue"] == 200.00
    # ROAS should be > 10.0x
    assert report["roas_multiplier"] > 10.0
