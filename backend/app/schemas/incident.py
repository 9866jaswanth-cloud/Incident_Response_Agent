"""Pydantic schemas for Incident ingestion, response, and confirmation."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class IncidentBase(BaseModel):
    title: str = Field(..., description="Short title describing the incident")
    service: str = Field(..., description="Service name experiencing the incident")
    severity: str = Field(..., description="P1-Critical, P2-High, P3-Medium, P4-Low")
    error_message: str = Field(..., description="Primary error message")
    symptoms: List[str] = Field(default_factory=list, description="Observed symptom bullet points")
    logs: str = Field(..., description="Recent error and diagnostic logs")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Key metrics like latency, error rate")
    recent_changes: str = Field("No recent changes recorded.", description="Recent deployments or commits")
    stack_trace: Optional[str] = Field(None, description="Optional stack trace")
    environment: str = Field("production-us-east-1", description="Target environment")


class IncidentCreate(IncidentBase):
    id: Optional[str] = Field(None, description="Optional custom ID like INC-045. Auto-generated if omitted.")


class IncidentConfirmRequest(BaseModel):
    status: str = Field("confirmed", description="'confirmed' or 'rejected'")
    confirmed_root_cause: Optional[str] = Field(None, description="Human-verified root cause")
    approved_resolution: Optional[str] = Field(None, description="Human-approved resolution steps")
    post_mortem_lesson: Optional[str] = Field(None, description="Key takeaway or prevention advice")
    notes: Optional[str] = Field(None, description="Optional SRE engineer notes")
    investigation_steps: Optional[List[str]] = Field(default_factory=list, description="Steps taken by SRE to isolate problem")
    corrected_root_cause: Optional[str] = Field(None, description="Optional corrected root cause overrule")
    corrected_resolution: Optional[str] = Field(None, description="Optional corrected resolution overrule")


class IncidentConfirmResponse(BaseModel):
    incident_id: str
    status: str  # "confirmed_and_retained", "rejected", "retained_with_corrections", "already_retained"
    retained_to_hindsight: bool
    bank_id: Optional[str] = None
    hindsight_memory_id: Optional[str] = None
    confirmed_root_cause: Optional[str] = None
    confirmed_resolution: Optional[str] = None
    message: str
    retained_post_mortem_preview: Optional[str] = None
    audit_log_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)



class IncidentResponse(IncidentBase):
    id: str
    status: str
    confirmed_root_cause: Optional[str] = None
    confirmed_resolution: Optional[str] = None
    investigation_steps: Optional[List[str]] = None
    post_mortem_lesson: Optional[str] = None
    retained_to_hindsight: bool = False
    retained_at: Optional[datetime] = None
    hindsight_memory_id: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class IncidentListResponse(BaseModel):
    total: int
    items: List[IncidentResponse]
