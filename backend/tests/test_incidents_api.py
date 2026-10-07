"""Tests for the Incidents API router."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import async_session_factory
from app.services.seed_service import seed_incidents


@pytest.fixture(autouse=True)
async def ensure_db_seeded():
    async with async_session_factory() as session:
        await seed_incidents(session, force_reload=True)


@pytest.mark.asyncio
async def test_list_incidents():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/incidents")
        assert res.status_code == 200
        data = res.json()
        assert "total" in data
        assert "items" in data
        assert data["total"] >= 35
        assert len(data["items"]) >= 35

        # Check item structure
        first = data["items"][0]
        assert "id" in first
        assert "title" in first
        assert "service" in first
        assert "severity" in first
        assert "status" in first
        assert "retained_to_hindsight" in first


@pytest.mark.asyncio
async def test_filter_incidents_by_severity():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/incidents?severity=P1-Critical")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] > 0
        for item in data["items"]:
            assert item["severity"] == "P1-Critical"


@pytest.mark.asyncio
async def test_get_incident_by_id():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/incidents/INC-001")
        assert res.status_code == 200
        item = res.json()
        assert item["id"] == "INC-001"
        assert item["service"] == "Payment API"
        assert "Connection Pool Exhaustion" in item["title"]


@pytest.mark.asyncio
async def test_get_nonexistent_incident():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/incidents/INC-999-DOES-NOT-EXIST")
        assert res.status_code == 404


@pytest.mark.asyncio
async def test_reset_demo_state():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/incidents/reset-demo")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert "INC-001" in data["demo_incidents"]
        assert "INC-002" in data["demo_incidents"]
        assert "INC-003" in data["demo_incidents"]


@pytest.mark.asyncio
async def test_spa_static_files_served():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/")
        assert res.status_code == 200
        assert "Incident Response Agent" in res.text
