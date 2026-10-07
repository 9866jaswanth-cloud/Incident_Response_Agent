"""API routes for Hindsight Memory status, timeline, and demo verification."""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.incident import Incident
from app.models.memory_log import MemoryAuditLog
from app.schemas.memory import (
    MemoryStatusResponse,
    MemoryTimelineEvent,
    MemoryRecallPreviewRequest,
    MemoryRecallPreviewResponse,
)
from app.services.hindsight_service import (
    HindsightService,
    HindsightUnavailableError,
    hindsight_service,
)

router = APIRouter(prefix="/memory", tags=["Hindsight Memory"])


@router.get("/status", response_model=MemoryStatusResponse)
async def get_memory_status():
    """
    Check the real connection status of the Hindsight server.
    Reports connected=True only if the real Hindsight server responded.
    """
    info = await hindsight_service.check_connection()
    return MemoryStatusResponse(
        connected=info["connected"],
        hindsight_base_url=info["base_url"],
        bank_id=info["bank_id"],
        version=info.get("version"),
        mode=info["mode"],
        message=info["message"],
    )


@router.post("/test-demo-retain")
async def demo_retain_incident(
    incident_id: str = Query("INC-001", description="ID of incident to retain"),
    db: AsyncSession = Depends(get_db),
):
    """
    Demo/Test endpoint to retain an incident post-mortem into Hindsight.
    Stores structured post-mortem for INC-001 in memory bank 'incident-response-bank'.
    """
    status_info = await hindsight_service.check_connection()
    if not status_info["connected"]:
        raise HTTPException(
            status_code=503,
            detail=f"Real Hindsight server is not reachable: {status_info['message']}",
        )

    incident = await db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found in database.")

    try:
        response = await hindsight_service.aretain(incident)
        incident.retained_to_hindsight = True
        await db.commit()

        # Log to audit trail
        log_entry = MemoryAuditLog(
            operation="RETAIN",
            bank_id=hindsight_service.bank_id,
            incident_id=incident_id,
            query_or_content=hindsight_service.format_incident_post_mortem(incident)[:500],
            results_summary=f"Success: {response.success}, Items: {response.items_count}",
            status="SUCCESS",
        )
        db.add(log_entry)
        await db.commit()

        return {
            "status": "success",
            "operation": "RETAIN",
            "incident_id": incident_id,
            "bank_id": hindsight_service.bank_id,
            "hindsight_response": {
                "success": response.success,
                "items_count": response.items_count,
                "bank_id": response.bank_id,
            },
            "retained_post_mortem_preview": hindsight_service.format_incident_post_mortem(incident)[:300] + "...",
        }
    except HindsightUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/test-demo-recall")
async def demo_recall_incident(
    query: str = Query(
        "Payment API p99 latency elevated to 8.2s with connection pool exhaustion and database timeout",
        description="Query representing INC-002 symptoms",
    ),
    budget: str = Query("mid", description="Recall depth/budget"),
    db: AsyncSession = Depends(get_db),
):
    """
    Demo/Test endpoint to recall historical incidents from Hindsight.
    Searches for related precedents using INC-002 symptoms without the exact INC-001 text.
    """
    status_info = await hindsight_service.check_connection()
    if not status_info["connected"]:
        raise HTTPException(
            status_code=503,
            detail=f"Real Hindsight server is not reachable: {status_info['message']}",
        )

    try:
        response = await hindsight_service.arecall(query=query, budget=budget)
        results = response.results if response and response.results else []

        recalled_items = []
        for r in results:
            item = {
                "id": r.id,
                "text": r.text,
                "type": getattr(r, "type", None),
                "entities": getattr(r, "entities", []),
                "metadata": getattr(r, "metadata", {}),
                "relevance_label": "Relevant historical precedent",
            }
            # Only include genuine scores if provided by Hindsight
            scores = getattr(r, "scores", None)
            if scores is not None:
                item["scores"] = str(scores)
            recalled_items.append(item)

        # Log to audit trail
        log_entry = MemoryAuditLog(
            operation="RECALL",
            bank_id=hindsight_service.bank_id,
            query_or_content=query,
            results_summary=f"Retrieved {len(recalled_items)} memories from Hindsight",
            status="SUCCESS",
        )
        db.add(log_entry)
        await db.commit()

        return {
            "status": "success",
            "operation": "RECALL",
            "query": query,
            "bank_id": hindsight_service.bank_id,
            "recalled_count": len(recalled_items),
            "memories": recalled_items,
        }
    except HindsightUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/timeline", response_model=List[MemoryTimelineEvent])
async def get_memory_timeline(
    limit: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve the chronological audit log of all Hindsight memory operations."""
    stmt = select(MemoryAuditLog).order_by(desc(MemoryAuditLog.timestamp)).limit(limit)
    res = await db.execute(stmt)
    records = res.scalars().all()
    return records
