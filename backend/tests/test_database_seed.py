"""Tests for Database Schema, Models, and Synthetic Dataset Seeding."""

import pytest
import pytest_asyncio
from sqlalchemy import select
from app.core.database import engine, Base, async_session_factory
from app.models.incident import Incident, Runbook, Analysis
from app.models.memory_log import MemoryAuditLog
from app.services.seed_service import seed_runbooks, seed_incidents, reset_demo_state
from app.schemas.incident import IncidentResponse


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Keep db intact for local testing


@pytest.mark.asyncio
async def test_seed_runbooks():
    async with async_session_factory() as session:
        count = await seed_runbooks(session)
        assert count >= 0  # May be 0 if already seeded or > 0 on first run

        result = await session.execute(select(Runbook))
        runbooks = result.scalars().all()
        assert len(runbooks) >= 8

        # Verify Payment API SOP
        pay_rb = await session.get(Runbook, "RB-PAY-01")
        assert pay_rb is not None
        assert pay_rb.service == "Payment API"
        assert "HikariCP" in pay_rb.standard_operating_procedure


@pytest.mark.asyncio
async def test_seed_synthetic_incidents():
    async with async_session_factory() as session:
        await seed_incidents(session, force_reload=True)


        result = await session.execute(select(Incident))
        incidents = result.scalars().all()
        assert len(incidents) >= 35

        # Verify primary demo incidents
        inc1 = await session.get(Incident, "INC-001")
        assert inc1 is not None
        assert inc1.service == "Payment API"
        assert inc1.severity == "P1-Critical"
        assert len(inc1.symptoms) >= 3
        assert inc1.metrics["p99_latency_ms"] > 8000
        assert "HikariPool" in inc1.logs

        # Pydantic schema conversion verification
        inc1_dto = IncidentResponse.model_validate(inc1)
        assert inc1_dto.id == "INC-001"
        assert inc1_dto.metrics["active_connections"] == 10

        inc2 = await session.get(Incident, "INC-002")
        assert inc2 is not None
        assert inc2.service == "Payment API"
        assert inc2.status == "Investigating"

        inc3 = await session.get(Incident, "INC-003")
        assert inc3 is not None
        assert inc3.service == "Order Service"


@pytest.mark.asyncio
async def test_reset_demo_state():
    async with async_session_factory() as session:
        res = await reset_demo_state(session)
        assert res["status"] == "success"

        inc1 = await session.get(Incident, "INC-001")
        assert inc1.status == "Investigating"
        assert inc1.retained_to_hindsight is False

        inc2 = await session.get(Incident, "INC-002")
        assert inc2.status == "Investigating"
        assert inc2.confirmed_root_cause is None

        inc3 = await session.get(Incident, "INC-003")
        assert inc3.status == "Investigating"
