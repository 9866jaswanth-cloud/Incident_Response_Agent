"""Pydantic schemas for AI Diagnostic Analysis and Evidence Provenance."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict

EvidenceType = Literal["CURRENT EVIDENCE", "HISTORICAL PRECEDENT", "RUNBOOK", "MODEL INFERENCE"]


class Hypothesis(BaseModel):
    cause: str = Field(..., description="Hypothesized root cause")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    evidence_type: EvidenceType = Field(..., description="Origin of this conclusion")
    rationale: str = Field(..., description="Detailed technical justification citing logs or precedents")
    historical_incident_id: Optional[str] = Field(None, description="Referenced precedent ID if applicable")


class RecalledMemoryItem(BaseModel):
    id: Optional[str] = Field(None, description="Memory unit ID")
    incident_id: Optional[str] = Field(None, description="Precedent incident ID if available")
    service: Optional[str] = Field(None, description="Precedent service")
    symptoms: Optional[str] = Field(None, description="Precedent symptoms")
    root_cause: Optional[str] = Field(None, description="Confirmed historical root cause")
    resolution: Optional[str] = Field(None, description="Confirmed historical resolution")
    outcome: Optional[str] = Field(None, description="Historical outcome")
    relevance_label: str = Field(
        default="Relevant historical precedent",
        description="Descriptive relevance label (e.g., 'Strong Semantic Precedent', 'High Reranker Match')"
    )
    raw_text: str = Field(..., description="The recalled memory snippet from Hindsight")
    scores: Optional[Dict[str, float]] = Field(None, description="Genuine scores from Hindsight (final, reranker, semantic, keyword)")
    document_id: Optional[str] = Field(None, description="Original document ID from Hindsight")
    context: Optional[str] = Field(None, description="Context description from Hindsight")
    source: str = Field(default="HINDSIGHT", description="Memory system origin")


class RemediationStep(BaseModel):
    step: int = Field(..., description="Step sequence number")
    action: str = Field(..., description="Actionable command or configuration edit")
    verification: str = Field(..., description="Verification command or metric to observe")
    is_destructive: bool = Field(False, description="Flag for actions requiring strict scrutiny")
    requires_human_approval: bool = Field(True, description="Prototype safety requirement")


class DiagnosticTrace(BaseModel):
    current_incident: Dict[str, Any] = Field(default_factory=dict, description="Current incident telemetry and symptoms")
    hindsight_recall: Dict[str, Any] = Field(default_factory=dict, description="Hindsight recall query and retrieval metadata")
    historical_precedents: List[Dict[str, Any]] = Field(default_factory=list, description="Extracted historical precedents")
    evidence_synthesis: Dict[str, Any] = Field(default_factory=dict, description="Provenance breakdown of all evidence")
    root_cause_hypotheses: List[Dict[str, Any]] = Field(default_factory=list, description="Structured hypotheses with citations")
    recommended_remediation: List[Dict[str, Any]] = Field(default_factory=list, description="Remediation steps with human checkpoints")


class AnalysisResponse(BaseModel):
    id: str
    incident_id: str
    summary: str
    hypotheses: List[Hypothesis]
    recalled_memories: List[RecalledMemoryItem]
    recommended_investigation: List[str]
    remediation_plan: List[RemediationStep]
    diagnostic_trace: Optional[DiagnosticTrace] = Field(None, description="Full diagnostic reasoning trace")
    mode: str = Field("with_memory", description="'with_memory' or 'without_memory'")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

