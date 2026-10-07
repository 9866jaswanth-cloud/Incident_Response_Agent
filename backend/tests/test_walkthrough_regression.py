"""Integration test verifying the 3-incident end-to-end learning walkthrough."""

import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_end_to_end_walkthrough_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Reset to clean baseline
        r_reset = await client.post("/api/incidents/reset-demo")
        assert r_reset.status_code == 200

        # STEP 1: INC-001 Cold Start
        r_ana1 = await client.post("/api/agent/analyze/INC-001")
        assert r_ana1.status_code == 200
        ana1 = r_ana1.json()
        assert len(ana1["hypotheses"]) > 0

        r_conf1 = await client.post("/api/agent/confirm/INC-001", json={
            "status": "confirmed",
            "confirmed_root_cause": "Database connection pool exhaustion under sudden traffic spike",
            "approved_resolution": "Increase HikariCP maximumPoolSize from 10 to 50 in Helm values and tune connection timeout to 3000ms",
            "post_mortem_lesson": "Always size connection pools with headroom for flash sale bursts and configure non-blocking connection timeouts."
        })
        assert r_conf1.status_code == 200
        conf1 = r_conf1.json()
        assert conf1["retained_to_hindsight"] is True
        assert conf1["bank_id"] == "incident-response-bank"

        # STEP 2: INC-002 Recalls INC-001
        r_iso2 = await client.post("/api/agent/analyze-isolated/INC-002")
        assert r_iso2.status_code == 200
        iso2 = r_iso2.json()
        assert len(iso2["recalled_memories"]) == 0

        r_ana2 = await client.post("/api/agent/analyze/INC-002")
        assert r_ana2.status_code == 200
        ana2 = r_ana2.json()
        assert len(ana2["recalled_memories"]) > 0
        top_hyp2 = ana2["hypotheses"][0]
        assert top_hyp2["evidence_type"] == "HISTORICAL PRECEDENT"
        assert top_hyp2.get("historical_incident_id") == "INC-001"

        r_conf2 = await client.post("/api/agent/confirm/INC-002", json={
            "status": "confirmed",
            "confirmed_root_cause": "Database connection pool misconfiguration under traffic surge",
            "approved_resolution": "Increase database connection pool size from 10 to 50 and set connection-timeout to 3000ms",
            "post_mortem_lesson": "Set pool size based on peak traffic expectations and monitor hikaricp_connections_idle."
        })
        assert r_conf2.status_code == 200
        conf2 = r_conf2.json()
        assert conf2["retained_to_hindsight"] is True

        # STEP 3: INC-003 Cross-Service Knowledge Transfer
        r_ana3 = await client.post("/api/agent/analyze/INC-003")
        assert r_ana3.status_code == 200
        ana3 = r_ana3.json()
        assert len(ana3["recalled_memories"]) > 0

        r_conf3 = await client.post("/api/agent/confirm/INC-003", json={
            "status": "confirmed",
            "confirmed_root_cause": "Order Service connection pool saturation caused by cascading queries",
            "approved_resolution": "Apply cross-service pool configuration standard: pool size 40 and 5s checkout timeout",
            "post_mortem_lesson": "Apply connection pool best practices across all tier-1 microservices."
        })
        assert r_conf3.status_code == 200
        conf3 = r_conf3.json()
        assert conf3["retained_to_hindsight"] is True

        # Verify Timeline
        r_time = await client.get("/api/memory/timeline?limit=25")
        assert r_time.status_code == 200

        # Reset back for clean demo
        await client.post("/api/incidents/reset-demo")
