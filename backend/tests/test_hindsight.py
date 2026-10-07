"""Tests for Hindsight Persistent Memory Integration (Phase 3).

Separates:
1. Configuration tests
2. SDK & Client initialization tests
3. Structured post-mortem formatting tests (INC-001)
4. Offline / unavailable error handling tests (Strict honesty: no fake memory)
5. FastAPI /api/memory/status endpoint test
6. Real end-to-end integration test (exercising live Hindsight when reachable)
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.core.config import settings
from app.main import app
from app.services.hindsight_service import (
    HindsightService,
    HindsightUnavailableError,
    hindsight_service,
)
from hindsight_client import (
    Hindsight,
    RetainResponse,
    RecallResponse,
    RecallResult,
)


@pytest.mark.asyncio
async def test_hindsight_configuration():
    """Verify Hindsight configuration settings."""
    assert settings.HINDSIGHT_BANK_ID == "incident-response-bank"
    assert settings.HINDSIGHT_BASE_URL.startswith("http")
    assert hindsight_service.bank_id == "incident-response-bank"


@pytest.mark.asyncio
async def test_hindsight_client_initialization():
    """Verify that HindsightService initializes the official Hindsight SDK."""
    service = HindsightService(
        base_url="http://127.0.0.1:8888",
        api_key="test-key",
        bank_id="test-bank",
    )
    client = await service.get_client()

    assert isinstance(client, Hindsight)
    assert hasattr(client, "aretain")
    assert hasattr(client, "arecall")
    assert hasattr(client, "areflect")
    assert hasattr(client, "aclose")
    assert hasattr(client, "aget_version")

    await service.aclose()


def test_hindsight_post_mortem_formatting():
    """
    Verify INC-001 post-mortem content formatting.
    Must contain all essential fields for Hindsight memory retention:
    incident ID, service, symptoms, telemetry/evidence, root cause,
    investigation steps, resolution, outcome, lessons learned.
    """
    inc1 = {
        "id": "INC-001",
        "service": "Payment API",
        "severity": "P1-Critical",
        "symptoms": [
            "Payment API p99 latency spiked from 195ms to 8.4 seconds",
            "Database connection acquisition timeouts (5000ms)",
            "HikariCP pool exhausted (10/10 active connections locked)"
        ],
        "logs": "com.zaxxer.hikari.pool.HikariPool - Connection is not available, request timed out after 5002ms",
        "metrics": {"p99_latency_ms": 8420, "active_connections": 10, "max_pool_size": 10},
        "confirmed_root_cause": "Database connection pool misconfiguration. Under 500 RPS traffic, maximum pool size was constrained to 10 connections.",
        "investigation_steps": [
            "1. Verified PostgreSQL RDS CPU was low (38%), ruling out DB server crash.",
            "2. Inspected HikariCP pool metrics in Grafana; saw all 10 connections continuously occupied.",
            "3. Reviewed Helm deployment diff for commit #c4b8109."
        ],
        "confirmed_resolution": "Increased database connection pool max_size from 10 to 50 in Helm values and set connection-timeout to 3000ms.",
        "post_mortem_lesson": "Always validate connection pool capacity against peak concurrency requirements during load spikes.",
        "environment": "production-us-east-1"
    }

    formatted = HindsightService.format_incident_post_mortem(inc1)

    assert "INC-001" in formatted
    assert "Payment API" in formatted
    assert "P1-Critical" in formatted
    assert "HikariCP pool exhausted" in formatted
    assert "Database connection pool misconfiguration" in formatted
    assert "Increased database connection pool max_size from 10 to 50" in formatted
    assert "Post-Mortem Lessons Learned" in formatted
    assert "Always validate connection pool capacity" in formatted


@pytest.mark.asyncio
async def test_hindsight_offline_reporting():
    """
    Test strict reporting when the real Hindsight server is not running.
    Must NOT silently pretend or report connected=True.
    """
    # Point to an unused loopback port
    service = HindsightService(
        base_url="http://127.0.0.1:59999",
        bank_id="incident-response-bank",
    )
    status = await service.check_connection()

    assert status["connected"] is False
    assert status["mode"] == "UNAVAILABLE"
    assert "NOT reachable" in status["message"]
    assert status["bank_id"] == "incident-response-bank"

    # Retain/recall attempts must raise HindsightUnavailableError
    with pytest.raises(HindsightUnavailableError):
        await service.arecall(query="Payment API latency spike")

    await service.aclose()


@pytest.mark.asyncio
async def test_api_memory_status_endpoint():
    """Test the GET /api/memory/status FastAPI endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/memory/status")
        assert response.status_code == 200

        data = response.json()
        assert "connected" in data
        assert "hindsight_base_url" in data
        assert data["bank_id"] == "incident-response-bank"
        assert data["mode"] in ["REAL_HINDSIGHT", "UNAVAILABLE"]


@pytest.mark.asyncio
async def test_real_hindsight_live_integration():
    """
    Integration test executing real retain and recall against Hindsight when online.
    If the server is offline, this test verifies the explicit offline detection.
    """
    status = await hindsight_service.check_connection()
    if not status["connected"]:
        pytest.skip(
            f"Real Hindsight server is offline at {hindsight_service.base_url}. "
            "Skipping live network calls as per Requirement 8."
        )


    # When real Hindsight is online:
    # 1. Retain INC-001 structured post-mortem
    inc1 = {
        "id": "INC-001",
        "service": "Payment API",
        "severity": "P1-Critical",
        "symptoms": ["Latency 8.4s", "Database connection pool timeout", "HikariCP 10/10 exhausted"],
        "logs": "Connection is not available, request timed out after 5002ms",
        "metrics": {"active_connections": 10},
        "confirmed_root_cause": "Database connection pool misconfiguration (max_connections set to 10)",
        "investigation_steps": ["1. Checked pool saturation.", "2. Checked PostgreSQL pg_stat_activity."],
        "confirmed_resolution": "Increase database connection pool size from 10 to 50",
        "post_mortem_lesson": "Always scale connection pool size with concurrent traffic volume.",
        "environment": "production-us-east-1"
    }

    retain_res = await hindsight_service.aretain(inc1)
    assert retain_res.success is True
    assert retain_res.bank_id == "incident-response-bank"

    # 2. Recall using INC-002 symptoms WITHOUT the exact INC-001 text
    query = "Payment API checkout reporting high latency 8.2s with connection pool exhaustion and database timeout"
    recall_res = await hindsight_service.arecall(query=query, budget="mid")

    assert recall_res is not None
    assert isinstance(recall_res.results, list)
    assert len(recall_res.results) > 0

    # Verify that the recalled memories contain relevant incident knowledge
    recalled_texts = [r.text.lower() for r in recall_res.results]
    assert any("latency" in t or "connection pool" in t or "inc-001" in t for t in recalled_texts)

