"""Phase 6 Comprehensive Tests: Human Confirmation -> Hindsight Retain Workflow.

Verifies:
1. Confirmed incident -> Real Hindsight retain + incident resolved + MemoryAuditLog.
2. Rejected recommendation -> No confirmed retain to Hindsight.
3. Corrected human resolution -> Corrected human data retained.
4. MemoryAuditLog creation and structure.
5. Memory timeline endpoint (GET /api/memory/timeline).
6. Real Hindsight retain against live local server.
7. Duplicate retention handling (idempotency).
8. Hindsight unavailable handling (graceful degradation).
9. Complete 3-incident learning loop:
   INC-001 (cold start -> confirm & retain)
   -> INC-002 (recalls INC-001 -> confirm & retain)
   -> INC-003 (recalls cross-service knowledge -> confirm & retain)
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from app.core.database import engine, Base, async_session_factory
from app.models.incident import Incident, Runbook
from app.models.memory_log import MemoryAuditLog
from app.services.hindsight_service import hindsight_service
from app.services.seed_service import seed_incidents, seed_runbooks
from app.main import app


@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    """Ensure clean tables and seeded synthetic data for each test run."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_factory() as session:
        await seed_runbooks(session)
        await seed_incidents(session)


@pytest.mark.asyncio
async def test_human_confirmation_triggers_retain_and_resolves_incident():
    """Requirement 1 & 2: Human confirmation triggers Hindsight retain and updates DB."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        req_payload = {
            "status": "confirmed",
            "confirmed_root_cause": "Database connection pool misconfiguration (limit 10 under 500 RPS traffic)",
            "approved_resolution": "Increased database connection pool max_size from 10 to 50 in Helm values and set connection-timeout to 3000ms",
            "post_mortem_lesson": "Always validate connection pool capacity against peak concurrency requirements during load spikes.",
            "notes": "Verified by Lead SRE on duty.",
            "investigation_steps": [
                "1. Inspected HikariCP pool saturation metrics.",
                "2. Confirmed RDS PostgreSQL CPU was healthy at 34%.",
                "3. Scaled connection pool to 50 and verified 0 pending requests."
            ]
        }

        response = await client.post("/api/agent/confirm/INC-001", json=req_payload)
        assert response.status_code == 200
        data = response.json()

        assert data["incident_id"] == "INC-001"
        assert data["status"] in ["confirmed_and_retained", "confirmed_local_only"]
        assert data["confirmed_root_cause"] == req_payload["confirmed_root_cause"]
        assert data["confirmed_resolution"] == req_payload["approved_resolution"]
        assert data["audit_log_id"] is not None

        # Verify database record updated
        async with async_session_factory() as session:
            inc = await session.get(Incident, "INC-001")
            assert inc is not None
            assert inc.status == "Resolved"
            assert inc.resolved_at is not None
            assert inc.confirmed_root_cause == req_payload["confirmed_root_cause"]

            # Verify MemoryAuditLog record
            audit_entry = await session.get(MemoryAuditLog, data["audit_log_id"])
            assert audit_entry is not None
            assert audit_entry.operation == "RETAIN"
            assert audit_entry.incident_id == "INC-001"
            assert audit_entry.bank_id == hindsight_service.bank_id


@pytest.mark.asyncio
async def test_rejected_recommendation_never_retained_to_hindsight():
    """Requirement 3 & 4: If engineer rejects recommendation, it is NOT retained to memory."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch.object(hindsight_service, "aretain") as mock_retain:
            reject_payload = {
                "status": "rejected",
                "notes": "Hypothesis incorrect: Database connection pool was not the problem. It was an upstream auth token expiration bug."
            }

            response = await client.post("/api/agent/confirm/INC-001", json=reject_payload)
            assert response.status_code == 200
            data = response.json()

            assert data["incident_id"] == "INC-001"
            assert data["status"] == "rejected"
            assert data["retained_to_hindsight"] is False
            assert "rejected" in data["message"].lower()

            # Ensure Hindsight aretain was NEVER called
            mock_retain.assert_not_called()

            # Verify database shows rejection and audit log reflects it
            async with async_session_factory() as session:
                inc = await session.get(Incident, "INC-001")
                assert inc.retained_to_hindsight is False
                assert inc.status == "Investigation Rejected"

                stmt = select(MemoryAuditLog).where(
                    MemoryAuditLog.incident_id == "INC-001",
                    MemoryAuditLog.operation == "REJECTION"
                )
                res = await session.execute(stmt)
                audit = res.scalars().first()
                assert audit is not None
                assert audit.status == "REJECTED"


@pytest.mark.asyncio
async def test_human_correction_overrules_ai_and_retains_corrected_data():
    """Requirement 4: When human overrules AI with corrected info, the corrected info is retained."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        corrected_payload = {
            "status": "confirmed",
            "corrected_root_cause": "Human verified: Stale DNS resolution in CoreDNS cache routing to deprecated database replica",
            "corrected_resolution": "Flushed CoreDNS cluster cache and updated RDS endpoint CNAME",
            "post_mortem_lesson": "Set DNS TTL to 5s on RDS cluster endpoints.",
            "notes": "Overruled initial AI hypothesis."
        }

        response = await client.post("/api/agent/confirm/INC-001", json=corrected_payload)
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "retained_with_corrections"
        assert data["confirmed_root_cause"] == corrected_payload["corrected_root_cause"]
        assert data["confirmed_resolution"] == corrected_payload["corrected_resolution"]

        # Check database holds corrected values
        async with async_session_factory() as session:
            inc = await session.get(Incident, "INC-001")
            assert inc.confirmed_root_cause == corrected_payload["corrected_root_cause"]
            assert inc.confirmed_resolution == corrected_payload["corrected_resolution"]


@pytest.mark.asyncio
async def test_duplicate_retention_is_idempotent():
    """Requirement 11: Duplicate retention calls are handled cleanly without error."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        req = {
            "status": "confirmed",
            "confirmed_root_cause": "Database connection pool misconfiguration",
            "approved_resolution": "Increase max_pool_size from 10 to 50"
        }

        # First confirmation
        resp1 = await client.post("/api/agent/confirm/INC-001", json=req)
        assert resp1.status_code == 200

        # Mark retained in DB explicitly if offline in test
        async with async_session_factory() as session:
            inc = await session.get(Incident, "INC-001")
            inc.retained_to_hindsight = True
            await session.commit()

        # Duplicate confirmation call
        resp2 = await client.post("/api/agent/confirm/INC-001", json=req)
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["status"] == "already_retained"
        assert data2["retained_to_hindsight"] is True
        assert "already been retained" in data2["message"]


@pytest.mark.asyncio
async def test_memory_timeline_endpoint():
    """Requirement 8: GET /api/memory/timeline returns chronological audit events."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create a retain event and a recall event
        await client.post("/api/agent/confirm/INC-001", json={
            "status": "confirmed",
            "confirmed_root_cause": "Pool exhausted",
            "approved_resolution": "Scaled pool"
        })

        # Query timeline
        resp = await client.get("/api/memory/timeline?limit=10")
        assert resp.status_code == 200
        timeline = resp.json()
        assert len(timeline) >= 1

        first_event = timeline[0]
        assert "id" in first_event
        assert "operation" in first_event
        assert "bank_id" in first_event
        assert "timestamp" in first_event
        assert first_event["operation"] in ["RETAIN", "RECALL", "REJECTION"]


@pytest.mark.asyncio
async def test_hindsight_unavailable_handling_during_confirmation():
    """Requirement 10 & 11: When Hindsight is offline, confirmation succeeds locally with explicit fallback audit."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch.object(hindsight_service, "check_connection", return_value={"connected": False, "message": "Server offline"}):
            req = {
                "status": "confirmed",
                "confirmed_root_cause": "Database connection pool misconfiguration",
                "approved_resolution": "Increase max_pool_size from 10 to 50"
            }

            resp = await client.post("/api/agent/confirm/INC-001", json=req)
            assert resp.status_code == 200
            data = resp.json()

            assert data["incident_id"] == "INC-001"
            assert data["status"] == "confirmed_local_only"
            assert "offline" in data["message"].lower()

            # Audit log records OFFLINE_FALLBACK
            async with async_session_factory() as session:
                stmt = select(MemoryAuditLog).where(
                    MemoryAuditLog.incident_id == "INC-001",
                    MemoryAuditLog.status == "OFFLINE_FALLBACK"
                )
                res = await session.execute(stmt)
                audit = res.scalars().first()
                assert audit is not None


@pytest.mark.asyncio
async def test_full_three_incident_organizational_learning_loop():
    """
    Requirement 6: Complete 3-incident learning story:
    INC-001 (Payment API): Cold start analyze -> human confirms -> RETAIN
    INC-002 (Payment API): Recalls INC-001 -> informed recommendation -> human confirms -> RETAIN
    INC-003 (Order Service): Recalls cross-service pool knowledge -> informed recommendation -> human confirms -> RETAIN
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Check if real Hindsight is online
        conn = await hindsight_service.check_connection()
        if not conn["connected"]:
            pytest.skip("Real Hindsight server not online; skipping live 3-incident loop.")

        # ==========================================
        # STEP 1: INC-001 (Payment API - First Failure)
        # ==========================================
        # 1a. Analyze INC-001
        res1_analyze = await client.post("/api/agent/analyze/INC-001")
        assert res1_analyze.status_code == 200
        d1_analyze = res1_analyze.json()
        assert d1_analyze["incident_id"] == "INC-001"
        # No prior precedent
        d1_types = [h["evidence_type"] for h in d1_analyze["hypotheses"]]
        assert "HISTORICAL PRECEDENT" not in d1_types

        # 1b. Human Engineer confirms INC-001 diagnosis and resolution -> RETAIN
        res1_confirm = await client.post("/api/agent/confirm/INC-001", json={
            "status": "confirmed",
            "confirmed_root_cause": "Database connection pool misconfiguration (limit 10 under 500 RPS traffic)",
            "approved_resolution": "Increased database connection pool max_size from 10 to 50 in Helm values and set connection-timeout to 3000ms",
            "post_mortem_lesson": "Always scale connection pool size with concurrent traffic volume.",
            "notes": "Verified in staging and applied to production."
        })
        assert res1_confirm.status_code == 200
        d1_confirm = res1_confirm.json()
        assert d1_confirm["retained_to_hindsight"] is True

        # ==========================================
        # STEP 2: INC-002 (Payment API - Recurrent Failure)
        # ==========================================
        # 2a. Analyze INC-002 -> Recalls INC-001 from Hindsight
        res2_analyze = await client.post("/api/agent/analyze/INC-002")
        assert res2_analyze.status_code == 200
        d2_analyze = res2_analyze.json()
        assert d2_analyze["incident_id"] == "INC-002"
        assert len(d2_analyze["recalled_memories"]) > 0

        # Precedent was incorporated into reasoning
        d2_types = [h["evidence_type"] for h in d2_analyze["hypotheses"]]
        assert "HISTORICAL PRECEDENT" in d2_types
        hist_h = next(h for h in d2_analyze["hypotheses"] if h["evidence_type"] == "HISTORICAL PRECEDENT")
        assert hist_h["historical_incident_id"] == "INC-001"

        # 2b. Human confirms INC-002 -> RETAIN
        res2_confirm = await client.post("/api/agent/confirm/INC-002", json={
            "status": "confirmed",
            "confirmed_root_cause": "Database connection pool misconfiguration recurring after release v2.14.0 Helm rollback",
            "approved_resolution": "Applied pool max_size 50 permanently in base Helm chart values",
            "post_mortem_lesson": "Ensure values.yaml overrides are preserved in base deployment templates."
        })
        assert res2_confirm.status_code == 200
        d2_confirm = res2_confirm.json()
        assert d2_confirm["retained_to_hindsight"] is True

        # ==========================================
        # STEP 3: INC-003 (Order Service - Cross-Service Precedent)
        # ==========================================
        # 3a. Analyze INC-003 -> Recalls cross-service pool knowledge from Payment API precedents
        res3_analyze = await client.post("/api/agent/analyze/INC-003")
        assert res3_analyze.status_code == 200
        d3_analyze = res3_analyze.json()
        assert d3_analyze["incident_id"] == "INC-003"
        assert len(d3_analyze["recalled_memories"]) > 0

        # Cross-service precedent recognized
        d3_types = [h["evidence_type"] for h in d3_analyze["hypotheses"]]
        assert "HISTORICAL PRECEDENT" in d3_types
        cross_h = next(h for h in d3_analyze["hypotheses"] if h["evidence_type"] == "HISTORICAL PRECEDENT")
        assert cross_h["historical_incident_id"] in ["INC-001", "INC-002"]
        assert "Order" in cross_h["cause"] or "cross-service" in cross_h["cause"].lower() or "pool" in cross_h["cause"].lower()

        # 3b. Human confirms INC-003 -> RETAIN
        res3_confirm = await client.post("/api/agent/confirm/INC-003", json={
            "status": "confirmed",
            "confirmed_root_cause": "Order Service HikariCP connection pool limit (15) saturated under 6-replica marketing push",
            "approved_resolution": "Increased OrderHikariPool max_pool_size from 15 to 45 in Order Service Helm values",
            "post_mortem_lesson": "Scale replica connection pools in lockstep with total database max_connections ceiling."
        })
        assert res3_confirm.status_code == 200
        d3_confirm = res3_confirm.json()
        assert d3_confirm["retained_to_hindsight"] is True

        # ==========================================
        # STEP 4: Verify Memory Timeline
        # ==========================================
        res_timeline = await client.get("/api/memory/timeline?limit=25")
        assert res_timeline.status_code == 200
        timeline_events = res_timeline.json()
        assert len(timeline_events) >= 3

        retained_incidents = [e["incident_id"] for e in timeline_events if e["operation"] == "RETAIN"]
        assert "INC-001" in retained_incidents
        assert "INC-002" in retained_incidents
        assert "INC-003" in retained_incidents
