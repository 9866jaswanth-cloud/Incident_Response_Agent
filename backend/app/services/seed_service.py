"""Database seeding service for synthetic enterprise incidents and runbooks."""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import init_db
from app.models.incident import Incident, Analysis, Runbook
from app.models.memory_log import MemoryAuditLog

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
INCIDENTS_FILE = DATA_DIR / "synthetic_incidents.json"
RUNBOOKS_FILE = DATA_DIR / "runbooks.json"


async def seed_runbooks(session: AsyncSession) -> int:
    """Seeds standard operating procedures from runbooks.json."""
    if not RUNBOOKS_FILE.exists():
        return 0

    with open(RUNBOOKS_FILE, "r", encoding="utf-8") as f:
        runbooks_data = json.load(f)

    inserted = 0
    for item in runbooks_data:
        existing = await session.get(Runbook, item["id"])
        if not existing:
            rb = Runbook(
                id=item["id"],
                service=item["service"],
                title=item["title"],
                trigger_symptoms=item.get("trigger_symptoms", []),
                standard_operating_procedure=item.get("standard_operating_procedure", ""),
            )
            session.add(rb)
            inserted += 1

    await session.commit()
    return inserted


async def seed_incidents(session: AsyncSession, force_reload: bool = False) -> int:
    """Seeds 35 synthetic enterprise incidents from synthetic_incidents.json."""
    if not INCIDENTS_FILE.exists():
        return 0

    with open(INCIDENTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    incidents_list = data.get("incidents", [])
    inserted = 0

    for item in incidents_list:
        existing = await session.get(Incident, item["id"])
        if existing and not force_reload:
            continue

        created_dt = datetime.fromisoformat(item["created_at"]) if "created_at" in item else datetime.now(timezone.utc)

        if existing and force_reload:
            # Update fields
            existing.title = item["title"]
            existing.service = item["service"]
            existing.severity = item["severity"]
            existing.status = item["status"]
            existing.error_message = item["error_message"]
            existing.symptoms = item["symptoms"]
            existing.logs = item["logs"]
            existing.metrics = item["metrics"]
            existing.recent_changes = item.get("recent_changes", "")
            existing.stack_trace = item.get("stack_trace")
            existing.environment = item.get("environment", "production-us-east-1")
            existing.confirmed_root_cause = item.get("confirmed_root_cause")
            existing.confirmed_resolution = item.get("confirmed_resolution")
            existing.investigation_steps = item.get("investigation_steps", [])
            existing.post_mortem_lesson = item.get("post_mortem_lesson")
            existing.retained_to_hindsight = item.get("retained_to_hindsight", False)
        else:
            inc = Incident(
                id=item["id"],
                title=item["title"],
                service=item["service"],
                severity=item["severity"],
                status=item["status"],
                error_message=item["error_message"],
                symptoms=item["symptoms"],
                logs=item["logs"],
                metrics=item["metrics"],
                recent_changes=item.get("recent_changes", "No recent changes recorded."),
                stack_trace=item.get("stack_trace"),
                environment=item.get("environment", "production-us-east-1"),
                confirmed_root_cause=item.get("confirmed_root_cause"),
                confirmed_resolution=item.get("confirmed_resolution"),
                investigation_steps=item.get("investigation_steps", []),
                post_mortem_lesson=item.get("post_mortem_lesson"),
                retained_to_hindsight=item.get("retained_to_hindsight", False),
                created_at=created_dt,
            )
            session.add(inc)
            inserted += 1

    await session.commit()
    return inserted


async def reset_demo_state(session: AsyncSession) -> Dict[str, Any]:
    """
    Resets the database state for the primary 3-incident demonstration.
    - INC-001: Investigating, unconfirmed, un-retained.
    - INC-002: Investigating, unconfirmed, un-retained.
    - INC-003: Investigating, unconfirmed, un-retained.
    - Deletes all recorded AI analyses for INC-001, INC-002, INC-003.
    """
    # Delete analyses for demo incidents
    await session.execute(
        delete(Analysis).where(Analysis.incident_id.in_(["INC-001", "INC-002", "INC-003"]))
    )

    # Reset INC-001 (ready for initial cold-start analysis & human confirmation)
    inc1 = await session.get(Incident, "INC-001")
    if inc1:
        inc1.status = "Investigating"
        inc1.retained_to_hindsight = False
        inc1.retained_at = None
        inc1.hindsight_memory_id = None
        # Preserve root cause in seed reference, but mark status as investigating

    # Reset INC-002 (ready for recall from INC-001)
    inc2 = await session.get(Incident, "INC-002")
    if inc2:
        inc2.status = "Investigating"
        inc2.confirmed_root_cause = None
        inc2.confirmed_resolution = None
        inc2.retained_to_hindsight = False
        inc2.retained_at = None

    # Reset INC-003 (ready for cross-service pattern recall)
    inc3 = await session.get(Incident, "INC-003")
    if inc3:
        inc3.status = "Investigating"
        inc3.confirmed_root_cause = None
        inc3.confirmed_resolution = None
        inc3.retained_to_hindsight = False
        inc3.retained_at = None

    await session.commit()

    return {
        "status": "success",
        "message": "Demo state reset successfully. INC-001, INC-002, and INC-003 are clean and ready for step-by-step demonstration.",
        "demo_incidents": ["INC-001", "INC-002", "INC-003"]
    }


async def seed_all(session: AsyncSession) -> Dict[str, Any]:
    """Runs table initialization and complete dataset seeding."""
    await init_db()
    runbooks_count = await seed_runbooks(session)
    incidents_count = await seed_incidents(session)
    return {
        "runbooks_seeded": runbooks_count,
        "incidents_seeded": incidents_count,
    }
