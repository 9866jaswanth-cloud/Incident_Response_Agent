"""API routes for Incidents listing, inspection, and demo lifecycle management."""

import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.incident import Incident
from app.schemas.incident import IncidentResponse, IncidentListResponse
from app.services.seed_service import reset_demo_state, seed_incidents

logger = logging.getLogger("incidents_api")

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.get("", response_model=IncidentListResponse)
async def list_incidents(
    status: Optional[str] = Query(None, description="Filter by status (Investigating, Mitigated, Resolved, Closed)"),
    severity: Optional[str] = Query(None, description="Filter by severity (P1-Critical, P2-High, P3-Medium, P4-Low)"),
    service: Optional[str] = Query(None, description="Filter by service name"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List production incidents with optional filtering."""
    query = select(Incident)

    if status:
        query = query.where(Incident.status == status)
    if severity:
        query = query.where(Incident.severity == severity)
    if service:
        query = query.where(Incident.service == service)

    # Order by ID / creation
    query = query.order_by(Incident.id.asc()).offset(offset).limit(limit)
    res = await db.execute(query)
    items = res.scalars().all()

    # Get total count
    count_query = select(Incident)
    if status:
        count_query = count_query.where(Incident.status == status)
    if severity:
        count_query = count_query.where(Incident.severity == severity)
    if service:
        count_query = count_query.where(Incident.service == service)
    count_res = await db.execute(count_query)
    total = len(count_res.scalars().all())

    return IncidentListResponse(
        total=total,
        items=[IncidentResponse.model_validate(inc) for inc in items],
    )


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve full incident details by ID."""
    inc = await db.get(Incident, incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found.")
    return IncidentResponse.model_validate(inc)


@router.post("/reset-demo")
async def reset_demo(
    db: AsyncSession = Depends(get_db),
):
    """
    Reset demo incidents (INC-001, INC-002, INC-003) to fresh unconfirmed/un-retained state.
    Allows replaying the 3-step organizational learning story repeatedly.
    """
    result = await reset_demo_state(db)
    return result


@router.post("/seed-fresh")
async def seed_fresh(
    db: AsyncSession = Depends(get_db),
):
    """Reload all 35 synthetic incidents from disk."""
    count = await seed_incidents(db, force_reload=True)
    return {"status": "success", "reloaded_count": count}
