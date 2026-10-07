"""Phase 5 Comprehensive Tests: Recall -> Reasoning Integration.

Verifies:
1. Current incident evidence is included in diagnostic reasoning.
2. Hindsight recall is actively invoked for POST /api/agent/analyze/{incident_id}.
3. Returned Hindsight memories reach the reasoning layer.
4. Historical precedent is strictly separated and labeled as [HISTORICAL PRECEDENT].
5. The agent does not claim historical information is current evidence.
6. Isolated analysis does NOT call Hindsight and produces cold-start reasoning.
7. Hindsight unavailable behavior remains safe and explicit.
8. End-to-end 3-incident demo story (INC-001 cold start -> retain -> INC-002 memory-augmented).
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport

from app.core.database import engine, Base, async_session_factory
from app.models.incident import Incident, Runbook
from app.schemas.analysis import RecalledMemoryItem
from app.services.agent_service import agent_service
from app.services.hindsight_service import hindsight_service, HindsightUnavailableError
from app.services.seed_service import seed_incidents, seed_runbooks
from app.main import app


@pytest_asyncio.fixture(autouse=True)
async def setup_test_database():
    """Ensure database tables and synthetic seed data exist for each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_factory() as session:
        await seed_runbooks(session)
        await seed_incidents(session)


@pytest.mark.asyncio
async def test_current_evidence_included_in_reasoning():
    """Requirement 1: Verify that current incident telemetry, logs, and symptoms are included."""
    async with async_session_factory() as session:
        inc = await session.get(Incident, "INC-002")
        assert inc is not None

        analysis = await agent_service.analyze(
            incident=inc,
            recalled_memories=[],
            runbook=None,
            mode="without_memory",
        )

        # Check diagnostic trace contains current telemetry
        assert analysis.diagnostic_trace is not None
        current_data = analysis.diagnostic_trace.current_incident
        assert current_data["id"] == "INC-002"
        assert current_data["service"] == "Payment API"
        assert "latency" in current_data["error_message"].lower() or "pool" in current_data["error_message"].lower()
        assert len(current_data["symptoms"]) > 0
        assert "active_connections" in current_data["metrics"]

        # Current evidence hypothesis must reflect active pool saturation from metrics/logs
        current_hyp = next((h for h in analysis.hypotheses if h.evidence_type == "CURRENT EVIDENCE"), None)
        assert current_hyp is not None
        assert "connection" in current_hyp.cause.lower() or "timeout" in current_hyp.cause.lower()


@pytest.mark.asyncio
async def test_hindsight_recall_called_and_reaches_reasoning():
    """Requirements 2 & 3: Hindsight recall is called and returned memories reach the reasoning layer."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Patch arecall to verify it was called and return controlled memory item
        mock_recall_result = AsyncMock()
        mock_recall_result.results = [
            AsyncMock(
                id="mem-unit-001",
                text="Confirmed Root Cause: Database connection pool misconfiguration. Resolution: Increased max_size from 10 to 50.",
                document_id="INC-001",
                context="Post-mortem experience for incident INC-001 in Payment API",
                scores=AsyncMock(final=0.88, reranker=0.82, semantic=0.75, keyword=0.5),
            )
        ]

        with patch.object(hindsight_service, "arecall", return_value=mock_recall_result) as mock_recall:
            response = await client.post("/api/agent/analyze/INC-002")
            assert response.status_code == 200

            # Verify arecall was called
            mock_recall.assert_awaited_once()
            call_kwargs = mock_recall.await_args.kwargs
            assert "query" in call_kwargs
            assert "Payment API" in call_kwargs["query"]

            data = response.json()
            assert data["incident_id"] == "INC-002"

            # Verify memories reached reasoning layer
            assert len(data["recalled_memories"]) == 1
            assert data["recalled_memories"][0]["incident_id"] == "INC-001"
            assert data["recalled_memories"][0]["scores"]["final"] == 0.88

            # Verify historical precedent hypothesis was formed
            hist_hyp = next((h for h in data["hypotheses"] if h["evidence_type"] == "HISTORICAL PRECEDENT"), None)
            assert hist_hyp is not None

            assert hist_hyp["historical_incident_id"] == "INC-001"
            assert "INC-001" in hist_hyp["rationale"] or "pool" in hist_hyp["cause"].lower()


@pytest.mark.asyncio
async def test_provenance_separation_and_no_leakage():
    """Requirements 4 & 5: Precedent is labeled separately; historical info is not claimed as current evidence."""
    async with async_session_factory() as session:
        inc = await session.get(Incident, "INC-002")
        assert inc is not None

        mock_memory = RecalledMemoryItem(
            id="mem-001",
            incident_id="INC-001",
            service="Payment API",
            root_cause="Database connection pool misconfiguration",
            resolution="Increased database connection pool max_size from 10 to 50",
            relevance_label="High Semantic Precedent",
            raw_text="INC-001: Pool misconfiguration resolved by setting max_size to 50.",
            scores={"final": 0.85, "semantic": 0.78, "reranker": 0.81, "keyword": 0.4},
            source="HINDSIGHT",
        )

        analysis = await agent_service.analyze(
            incident=inc,
            recalled_memories=[mock_memory],
            runbook=None,
            mode="with_memory",
        )

        # 1. Distinct evidence types present
        evidence_types = [h.evidence_type for h in analysis.hypotheses]
        assert "HISTORICAL PRECEDENT" in evidence_types
        assert "CURRENT EVIDENCE" in evidence_types
        assert "MODEL INFERENCE" in evidence_types

        # 2. Historical hypothesis cites INC-001
        hist_h = next(h for h in analysis.hypotheses if h.evidence_type == "HISTORICAL PRECEDENT")
        assert hist_h.historical_incident_id == "INC-001"

        # 3. Current evidence hypothesis does NOT claim INC-001 is current evidence
        curr_h = next(h for h in analysis.hypotheses if h.evidence_type == "CURRENT EVIDENCE")
        assert curr_h.historical_incident_id is None
        assert "INC-001" not in curr_h.cause

        # 4. Remediation plan cites proven resolution from precedent
        actions = [step.action for step in analysis.remediation_plan]
        assert any("INC-001" in a or "max_pool_size" in a for a in actions)


@pytest.mark.asyncio
async def test_isolated_analysis_does_not_call_hindsight():
    """Requirement 6: Isolated analysis strictly does NOT call Hindsight."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch.object(hindsight_service, "arecall") as mock_recall:
            response = await client.post("/api/agent/analyze-isolated/INC-002")
            assert response.status_code == 200

            # MUST NOT have called Hindsight recall
            mock_recall.assert_not_called()

            data = response.json()
            assert data["mode"] == "without_memory"
            assert len(data["recalled_memories"]) == 0

            # Must NOT have any HISTORICAL PRECEDENT hypothesis
            evidence_types = [h["evidence_type"] for h in data["hypotheses"]]
            assert "HISTORICAL PRECEDENT" not in evidence_types


@pytest.mark.asyncio
async def test_hindsight_unavailable_behavior_remains_safe():
    """Requirement 7: If Hindsight is offline, analysis degrades safely to cold start without fake memory."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch.object(hindsight_service, "arecall", side_effect=HindsightUnavailableError("Server offline")):
            response = await client.post("/api/agent/analyze/INC-002")
            assert response.status_code == 200

            data = response.json()
            assert data["incident_id"] == "INC-002"
            # Degraded safely to empty recalled memories
            assert len(data["recalled_memories"]) == 0
            # Does not crash or invent fake memories
            assert len(data["hypotheses"]) >= 2
            evidence_types = [h["evidence_type"] for h in data["hypotheses"]]
            assert "HISTORICAL PRECEDENT" not in evidence_types


@pytest.mark.asyncio
async def test_end_to_end_demo_story_flow():
    """
    Requirement 8: The exact demo story:
    1. INC-001: First Payment API incident -> analyzed in cold-start mode.
    2. Retain INC-001 structured post-mortem into Hindsight.
    3. INC-002: Similar Payment API symptoms -> analyzed with Hindsight memory.
    4. INC-002 recalls INC-001 and generates precedent-informed recommendation.
    5. Compare against isolated INC-002 analysis to prove memory difference.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Step 1: Analyze INC-001 (Cold Start)
        resp1 = await client.post("/api/agent/analyze/INC-001")
        assert resp1.status_code == 200
        data1 = resp1.json()
        assert data1["incident_id"] == "INC-001"
        # INC-001 has no prior precedents
        types1 = [h["evidence_type"] for h in data1["hypotheses"]]
        assert "HISTORICAL PRECEDENT" not in types1

        # Step 2: Live retain INC-001 into Hindsight
        # (Using the real local Hindsight server running on port 8888)
        status = await hindsight_service.check_connection()
        if status["connected"]:
            inc1_payload = {
                "id": "INC-001",
                "service": "Payment API",
                "severity": "P1-Critical",
                "symptoms": ["Latency spiked to 8.4s", "HikariCP 10/10 connection pool locked"],
                "confirmed_root_cause": "Database connection pool misconfiguration (10 max connections under 500 RPS)",
                "confirmed_resolution": "Increased database connection pool max_size from 10 to 50 and set connection-timeout to 3000ms",
                "post_mortem_lesson": "Always scale connection pool size with concurrent traffic volume.",
                "environment": "production-us-east-1"
            }
            retain_res = await hindsight_service.aretain(inc1_payload)
            assert retain_res.success is True

            # Step 3: Analyze INC-002 with real memory recall
            resp2 = await client.post("/api/agent/analyze/INC-002")
            assert resp2.status_code == 200
            data2 = resp2.json()
            assert data2["incident_id"] == "INC-002"
            assert len(data2["recalled_memories"]) > 0

            # Step 4: Verify precedent influenced reasoning
            types2 = [h["evidence_type"] for h in data2["hypotheses"]]
            assert "HISTORICAL PRECEDENT" in types2
            hist_h = next(h for h in data2["hypotheses"] if h["evidence_type"] == "HISTORICAL PRECEDENT")
            assert hist_h["historical_incident_id"] == "INC-001"
            assert hist_h["confidence"] >= 0.85

            # Step 5: Verify isolated analysis on INC-002 lacks the precedent
            resp_iso = await client.post("/api/agent/analyze-isolated/INC-002")
            assert resp_iso.status_code == 200
            data_iso = resp_iso.json()
            types_iso = [h["evidence_type"] for h in data_iso["hypotheses"]]
            assert "HISTORICAL PRECEDENT" not in types_iso
            assert len(data_iso["recalled_memories"]) == 0
