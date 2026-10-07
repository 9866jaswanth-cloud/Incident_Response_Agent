import time
import logging
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.incident import Incident, Analysis, Runbook
from app.models.memory_log import MemoryAuditLog
from app.schemas.analysis import AnalysisResponse, RecalledMemoryItem
from app.schemas.incident import IncidentConfirmRequest, IncidentConfirmResponse
from app.services.agent_service import agent_service
from app.services.hindsight_service import hindsight_service, HindsightUnavailableError

logger = logging.getLogger("agent_api")

router = APIRouter(prefix="/agent", tags=["AI Incident Agent"])



@router.post("/analyze/{incident_id}", response_model=AnalysisResponse)
async def analyze_incident(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger the AI Agent diagnostic pipeline for an incident.
    1. Fetches current incident telemetry, logs, and metrics.
    2. Recalls historical incident memories from Hindsight.
    3. Finds relevant service Runbook SOP.
    4. Synthesizes evidence to produce grounded hypotheses and actionable remediation.
    5. Persists the analysis in the database.
    """
    incident = await db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found.")

    # 1. Fetch relevant runbook if available
    runbook_stmt = select(Runbook).where(Runbook.service == incident.service)
    runbook_res = await db.execute(runbook_stmt)
    runbook = runbook_res.scalars().first()

    # 2. Recall historical precedents from Hindsight using CURRENT incident evidence
    recalled_items: List[RecalledMemoryItem] = []
    try:
        symptoms_str = ", ".join(incident.symptoms) if isinstance(incident.symptoms, list) else str(incident.symptoms)
        query = f"Service: {incident.service}. Error: {incident.error_message}. Symptoms: {symptoms_str}"

        # Real Hindsight recall
        recall_response = await hindsight_service.arecall(query=query, budget="mid")

        if recall_response and recall_response.results:
            for r in recall_response.results:
                # Genuine scores from Hindsight
                scores_dict = None
                if getattr(r, "scores", None):
                    s = r.scores
                    scores_dict = {
                        "final": float(getattr(s, "final", 0.0) or 0.0),
                        "reranker": float(getattr(s, "reranker", 0.0) or 0.0),
                        "semantic": float(getattr(s, "semantic", 0.0) or 0.0),
                        "keyword": float(getattr(s, "keyword", 0.0) or 0.0),
                    }

                # Determine incident/document ID
                doc_id = getattr(r, "document_id", None)
                r_id = getattr(r, "id", None)
                inc_id = doc_id if doc_id and doc_id.startswith("INC-") else None
                if not inc_id:
                    import re
                    match = re.search(r"INC-\d+", (getattr(r, "context", "") or "") + " " + (getattr(r, "text", "") or ""))
                    if match:
                        inc_id = match.group(0)

                # IMPORTANT: A current incident cannot be a historical precedent for itself
                if inc_id == incident.id or doc_id == incident.id:
                    continue

                # Descriptive relevance label derived from genuine scores
                rel_label = "Historical Precedent"
                if scores_dict:
                    if scores_dict.get("reranker", 0) > 0.05 or scores_dict.get("semantic", 0) > 0.70:
                        rel_label = "High Semantic Precedent"
                    elif scores_dict.get("semantic", 0) > 0.45:
                        rel_label = "Corroborating Precedent"

                recalled_items.append(
                    RecalledMemoryItem(
                        id=r_id,
                        incident_id=inc_id,
                        service=incident.service,
                        symptoms=getattr(r, "context", None),
                        root_cause=None,
                        resolution=None,
                        relevance_label=rel_label,
                        raw_text=r.text,
                        scores=scores_dict,
                        document_id=doc_id,
                        context=getattr(r, "context", None),
                        source="HINDSIGHT",
                    )
                )
    except HindsightUnavailableError:
        logger.info(f"Hindsight server is offline. Running diagnostic analysis in cold-start mode for {incident_id}.")
    except Exception as e:
        logger.warning(f"Memory recall encountered error: {e}. Proceeding with current evidence.")

    # 3. Execute Diagnostic Synthesis
    analysis_dto = await agent_service.analyze(
        incident=incident,
        recalled_memories=recalled_items,
        runbook=runbook,
        mode="with_memory",
    )

    # 4. Persist analysis to database
    db_analysis = Analysis(
        id=analysis_dto.id,
        incident_id=incident.id,
        summary=analysis_dto.summary,
        hypotheses=[h.model_dump() for h in analysis_dto.hypotheses],
        recalled_memories=[m.model_dump() for m in analysis_dto.recalled_memories],
        recommended_investigation=analysis_dto.recommended_investigation,
        remediation_plan=[r.model_dump() for r in analysis_dto.remediation_plan],
        diagnostic_trace=analysis_dto.diagnostic_trace.model_dump() if analysis_dto.diagnostic_trace else {},
        mode=analysis_dto.mode,
    )
    db.add(db_analysis)
    await db.commit()

    return analysis_dto


@router.post("/analyze-isolated/{incident_id}", response_model=AnalysisResponse)
async def analyze_incident_isolated(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Run diagnostic analysis WITHOUT historical memory.
    Explicitly bypasses Hindsight recall. Used for comparative A/B evaluation against
    the memory-augmented agent.
    """
    incident = await db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found.")

    # Fetch runbook
    runbook_stmt = select(Runbook).where(Runbook.service == incident.service)
    runbook_res = await db.execute(runbook_stmt)
    runbook = runbook_res.scalars().first()

    # Analyze strictly in isolated mode (empty memories, no Hindsight call)
    analysis_dto = await agent_service.analyze(
        incident=incident,
        recalled_memories=[],
        runbook=runbook,
        mode="without_memory",
    )

    # Persist isolated analysis record
    db_analysis = Analysis(
        id=analysis_dto.id,
        incident_id=incident.id,
        summary=analysis_dto.summary,
        hypotheses=[h.model_dump() for h in analysis_dto.hypotheses],
        recalled_memories=[],
        recommended_investigation=analysis_dto.recommended_investigation,
        remediation_plan=[r.model_dump() for r in analysis_dto.remediation_plan],
        diagnostic_trace=analysis_dto.diagnostic_trace.model_dump() if analysis_dto.diagnostic_trace else {},
        mode="without_memory",
    )
    db.add(db_analysis)
    await db.commit()

    return analysis_dto



@router.get("/analysis/{incident_id}", response_model=Optional[AnalysisResponse])
async def get_latest_analysis(
    incident_id: str,
    mode: str = Query("with_memory", description="'with_memory' or 'without_memory'"),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve the latest recorded analysis for an incident."""
    stmt = (
        select(Analysis)
        .where(Analysis.incident_id == incident_id, Analysis.mode == mode)
        .order_by(desc(Analysis.created_at))
    )
    res = await db.execute(stmt)
    analysis_record = res.scalars().first()
    if not analysis_record:
        return None

    return AnalysisResponse(
        id=analysis_record.id,
        incident_id=analysis_record.incident_id,
        summary=analysis_record.summary,
        hypotheses=analysis_record.hypotheses,
        recalled_memories=analysis_record.recalled_memories,
        recommended_investigation=analysis_record.recommended_investigation,
        remediation_plan=analysis_record.remediation_plan,
        diagnostic_trace=analysis_record.diagnostic_trace,
        mode=analysis_record.mode,
        created_at=analysis_record.created_at,
    )


@router.post("/confirm/{incident_id}", response_model=IncidentConfirmResponse)
async def confirm_incident(
    incident_id: str,
    req: IncidentConfirmRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Human confirmation / rejection checkpoint before Hindsight retention.
    
    CRITICAL WORKFLOW RULES:
    1. NEVER automatically retain an AI hypothesis as confirmed organizational memory.
    2. ONLY after explicit human confirmation:
       - Update incident to Resolved with human-verified root cause and resolution.
       - Format structured post-mortem.
       - Call real Hindsight aretain().
       - Record MemoryAuditLog entry.
    3. If rejected:
       - Do NOT retain to Hindsight.
       - If human provides corrected root cause & resolution, retain the corrected information.
    4. Handles duplicate retentions gracefully and idempotently.
    5. Handles Hindsight unavailable safely.
    """
    incident = await db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found.")

    now = datetime.now(timezone.utc)

    # 1. Handle Rejection
    if req.status == "rejected":
        # If human did not provide a corrected resolution to retain:
        if not req.corrected_root_cause and not req.corrected_resolution:
            incident.status = "Investigation Rejected"
            
            # Audit log for human rejection
            audit_log = MemoryAuditLog(
                operation="REJECTION",
                bank_id=hindsight_service.bank_id,
                incident_id=incident.id,
                query_or_content=f"Human engineer rejected AI recommendations for {incident.id}. SRE Notes: {req.notes or 'None'}",
                results_summary="AI recommendations rejected by human operator. NOT retained to Hindsight organizational memory.",
                status="REJECTED",
                duration_ms=0.0,
                timestamp=now,
            )
            db.add(audit_log)
            await db.commit()
            await db.refresh(audit_log)

            return IncidentConfirmResponse(
                incident_id=incident.id,
                status="rejected",
                retained_to_hindsight=False,
                bank_id=hindsight_service.bank_id,
                confirmed_root_cause=None,
                confirmed_resolution=None,
                message="AI recommendation was rejected. No unconfirmed hypothesis was retained to Hindsight memory.",
                audit_log_id=audit_log.id,
            )

    # 2. Check for duplicate retention (idempotency)
    if incident.retained_to_hindsight:
        return IncidentConfirmResponse(
            incident_id=incident.id,
            status="already_retained",
            retained_to_hindsight=True,
            bank_id=hindsight_service.bank_id,
            hindsight_memory_id=incident.hindsight_memory_id,
            confirmed_root_cause=incident.confirmed_root_cause,
            confirmed_resolution=incident.confirmed_resolution,
            message=f"Incident {incident.id} has already been retained in Hindsight memory bank '{hindsight_service.bank_id}'.",
        )

    # 3. Determine confirmed or corrected root cause & resolution
    effective_root_cause = (
        req.corrected_root_cause
        or req.confirmed_root_cause
        or incident.confirmed_root_cause
    )
    effective_resolution = (
        req.corrected_resolution
        or req.approved_resolution
        or incident.confirmed_resolution
    )

    if not effective_root_cause or not effective_resolution:
        raise HTTPException(
            status_code=400,
            detail="A confirmed root cause and approved resolution must be provided for human confirmation.",
        )

    # 4. Update incident state in local database
    incident.confirmed_root_cause = effective_root_cause
    incident.confirmed_resolution = effective_resolution
    if req.post_mortem_lesson:
        incident.post_mortem_lesson = req.post_mortem_lesson
    if req.investigation_steps:
        incident.investigation_steps = req.investigation_steps
    incident.status = "Resolved"
    incident.resolved_at = now

    # 5. Format structured post-mortem document
    post_mortem_doc = hindsight_service.format_incident_post_mortem(incident)

    # 6. Retain into real Hindsight server
    t0 = time.time()
    retained_to_hindsight = False
    hindsight_memory_id = None
    audit_status = "SUCCESS"
    audit_summary = ""

    conn_status = await hindsight_service.check_connection()
    if conn_status.get("connected", False):
        try:
            retain_resp = await hindsight_service.aretain(incident)
            retained_to_hindsight = retain_resp.success
            hindsight_memory_id = getattr(retain_resp, "id", None) or f"{incident.id}-hindsight"
            incident.retained_to_hindsight = True
            incident.retained_at = now
            incident.hindsight_memory_id = hindsight_memory_id
            audit_summary = (
                f"Human-confirmed post-mortem successfully retained into Hindsight bank '{hindsight_service.bank_id}'. "
                f"Ingested {retain_resp.items_count} document(s)."
            )
        except Exception as e:
            logger.error(f"Hindsight aretain failed: {e}")
            audit_status = "FAILED"
            audit_summary = f"Hindsight retain error: {str(e)}"
    else:
        audit_status = "OFFLINE_FALLBACK"
        audit_summary = f"Real Hindsight server is offline at {hindsight_service.base_url}. Retention pending server availability."

    duration_ms = round((time.time() - t0) * 1000, 2)

    # 7. Record MemoryAuditLog entry
    audit_log = MemoryAuditLog(
        operation="RETAIN",
        bank_id=hindsight_service.bank_id,
        incident_id=incident.id,
        query_or_content=post_mortem_doc[:800],
        results_summary=audit_summary,
        status=audit_status,
        duration_ms=duration_ms,
        timestamp=now,
    )
    db.add(audit_log)
    await db.commit()
    await db.refresh(audit_log)

    is_corrected = bool(req.corrected_root_cause or req.corrected_resolution)
    status_label = "retained_with_corrections" if is_corrected else ("confirmed_and_retained" if retained_to_hindsight else "confirmed_local_only")
    user_msg = (
        f"Incident {incident.id} confirmed with human corrections and retained into Hindsight."
        if is_corrected
        else (
            f"Incident {incident.id} confirmed and permanently retained into Hindsight memory bank '{hindsight_service.bank_id}'."
            if retained_to_hindsight
            else f"Incident {incident.id} confirmed and resolved locally (Hindsight server currently offline; pending retention)."
        )
    )

    return IncidentConfirmResponse(
        incident_id=incident.id,
        status=status_label,
        retained_to_hindsight=incident.retained_to_hindsight,
        bank_id=hindsight_service.bank_id,
        hindsight_memory_id=incident.hindsight_memory_id,
        confirmed_root_cause=incident.confirmed_root_cause,
        confirmed_resolution=incident.confirmed_resolution,
        message=user_msg,
        retained_post_mortem_preview=post_mortem_doc[:350] + "...",
        audit_log_id=audit_log.id,
    )


