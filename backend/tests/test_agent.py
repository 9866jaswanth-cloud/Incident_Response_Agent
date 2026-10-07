"""Automated unit and integration tests for AI Incident Analysis Agent (Phase 4)."""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.core.database import engine, Base, async_session_factory
from app.models.incident import Incident, Runbook
from app.schemas.analysis import RecalledMemoryItem
from app.services.agent_service import agent_service
from app.services.seed_service import seed_incidents, seed_runbooks
from app.main import app


@pytest_asyncio.fixture(autouse=True)
async def setup_test_data():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_factory() as session:
        await seed_runbooks(session)
        await seed_incidents(session)


@pytest.mark.asyncio
async def test_agent_cold_start_analysis():
    """
    Test diagnostic analysis of INC-001 in cold start (without memory).
    Must generate summary, grounded hypotheses, investigation steps, and safe remediation.
    """
    async with async_session_factory() as session:
        inc1 = await session.get(Incident, "INC-001")
        assert inc1 is not None

        runbook = await session.get(Runbook, "RB-PAY-01")

        analysis = await agent_service.analyze(
            incident=inc1,
            recalled_memories=[],
            runbook=runbook,
            mode="without_memory",
        )

        assert analysis.incident_id == "INC-001"
        assert len(analysis.summary) > 20
        assert len(analysis.hypotheses) >= 2

        # Check evidence types in cold start: only CURRENT EVIDENCE or MODEL INFERENCE
        evidence_types = [h.evidence_type for h in analysis.hypotheses]
        assert "CURRENT EVIDENCE" in evidence_types
        assert "HISTORICAL PRECEDENT" not in evidence_types

        # Verify safe remediation requiring human approval
        assert len(analysis.remediation_plan) >= 1
        for step in analysis.remediation_plan:
            assert step.requires_human_approval is True
            assert step.is_destructive is False


@pytest.mark.asyncio
async def test_agent_memory_augmented_analysis():
    """
    Test diagnostic analysis of INC-002 with an INC-001 historical memory precedent.
    The agent must synthesize a hypothesis with evidence_type='HISTORICAL PRECEDENT'.
    """
    async with async_session_factory() as session:
        inc2 = await session.get(Incident, "INC-002")
        assert inc2 is not None

        # Simulate recalled memory of INC-001
        recalled = [
            RecalledMemoryItem(
                incident_id="INC-001",
                service="Payment API",
                symptoms="Connection pool exhaustion, latency spiked to 8.4s",
                root_cause="Database connection pool misconfiguration (limit 10 under 500 RPS)",
                resolution="Increased database connection pool max_size from 10 to 50",
                outcome="Latency normalized to 185ms baseline",
                relevance_label="Strong Historical Match",
                raw_text="Confirmed Root Cause: Database connection pool misconfiguration. Resolution: Increased max_size from 10 to 50.",
                source="HINDSIGHT",
            )
        ]

        analysis = await agent_service.analyze(
            incident=inc2,
            recalled_memories=recalled,
            runbook=None,
            mode="with_memory",
        )

        assert analysis.incident_id == "INC-002"
        assert len(analysis.recalled_memories) == 1
        assert analysis.recalled_memories[0].incident_id == "INC-001"

        # Check that historical precedent was recognized
        evidence_types = [h.evidence_type for h in analysis.hypotheses]
        assert "HISTORICAL PRECEDENT" in evidence_types

        # Top hypothesis should cite INC-001
        hist_hypothesis = next(h for h in analysis.hypotheses if h.evidence_type == "HISTORICAL PRECEDENT")
        assert hist_hypothesis.historical_incident_id == "INC-001"
        assert "INC-001" in hist_hypothesis.rationale or "pool" in hist_hypothesis.cause.lower()

        # Remediation plan cites previous resolution
        actions = [s.action for s in analysis.remediation_plan]
        assert any("INC-001" in a or "max_pool_size" in a or "connection pool" in a for a in actions)


@pytest.mark.asyncio
async def test_api_agent_analyze_endpoint():
    """Test the POST /api/agent/analyze/{incident_id} endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Trigger analysis on INC-001
        response = await client.post("/api/agent/analyze/INC-001")
        assert response.status_code == 200

        data = response.json()
        assert data["incident_id"] == "INC-001"
        assert len(data["hypotheses"]) >= 2
        assert len(data["remediation_plan"]) >= 1

        # 2. Query recorded analysis
        res_get = await client.get("/api/agent/analysis/INC-001?mode=with_memory")
        assert res_get.status_code == 200
        saved_data = res_get.json()
        assert saved_data is not None
        assert saved_data["incident_id"] == "INC-001"


@pytest.mark.asyncio
async def test_api_agent_isolated_analyze_endpoint():
    """Test the POST /api/agent/analyze-isolated/{incident_id} endpoint for A/B testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/agent/analyze-isolated/INC-002")
        assert response.status_code == 200

        data = response.json()
        assert data["incident_id"] == "INC-002"
        assert data["mode"] == "without_memory"
        assert len(data["recalled_memories"]) == 0
