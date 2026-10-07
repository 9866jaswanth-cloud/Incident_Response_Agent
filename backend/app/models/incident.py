"""Database ORM models for Incidents, Analyses, and Runbooks."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Incident(Base):
    """Represents a production incident."""

    __tablename__ = "incidents"

    id: str = Column(String(32), primary_key=True, index=True)
    title: str = Column(String(255), nullable=False)
    service: str = Column(String(64), nullable=False, index=True)
    severity: str = Column(String(16), nullable=False, index=True)  # P1-Critical, P2-High, P3-Medium, P4-Low
    status: str = Column(String(32), nullable=False, default="Investigating", index=True)  # Investigating, Mitigated, Resolved, Closed
    error_message: str = Column(Text, nullable=False)
    symptoms: List[str] = Column(JSON, nullable=False, default=list)
    logs: str = Column(Text, nullable=False)
    metrics: Dict[str, Any] = Column(JSON, nullable=False, default=dict)
    recent_changes: str = Column(Text, nullable=False, default="No recent deployments recorded.")
    stack_trace: Optional[str] = Column(Text, nullable=True)
    environment: str = Column(String(64), nullable=False, default="production-us-east-1")
    
    # Human confirmation & post-mortem fields
    confirmed_root_cause: Optional[str] = Column(Text, nullable=True)
    confirmed_resolution: Optional[str] = Column(Text, nullable=True)
    investigation_steps: Optional[List[str]] = Column(JSON, nullable=True, default=list)
    post_mortem_lesson: Optional[str] = Column(Text, nullable=True)

    # Hindsight Memory tracking
    retained_to_hindsight: bool = Column(Boolean, default=False, nullable=False)
    retained_at: Optional[datetime] = Column(DateTime, nullable=True)
    hindsight_memory_id: Optional[str] = Column(String(128), nullable=True)

    created_at: datetime = Column(DateTime, default=utcnow, nullable=False)
    resolved_at: Optional[datetime] = Column(DateTime, nullable=True)

    # Relationships
    analyses = relationship("Analysis", back_populates="incident", cascade="all, delete-orphan", order_by="desc(Analysis.created_at)")


class Analysis(Base):
    """Represents an AI diagnostic analysis run on an incident."""

    __tablename__ = "analyses"

    id: str = Column(String(36), primary_key=True)
    incident_id: str = Column(String(32), ForeignKey("incidents.id"), nullable=False, index=True)
    summary: str = Column(Text, nullable=False)
    
    # Grounded hypotheses list with evidence attribution
    # Schema: [{"cause": str, "confidence": float, "evidence_type": "CURRENT"|"HISTORICAL"|"RUNBOOK"|"INFERENCE", "rationale": str}]
    hypotheses: List[Dict[str, Any]] = Column(JSON, nullable=False, default=list)
    
    # Recalled precedents from Hindsight
    # Schema: [{"incident_id": str, "service": str, "symptoms": str, "root_cause": str, "resolution": str, "relevance_explanation": str}]
    recalled_memories: List[Dict[str, Any]] = Column(JSON, nullable=False, default=list)
    
    # Recommended steps
    recommended_investigation: List[str] = Column(JSON, nullable=False, default=list)
    remediation_plan: List[Dict[str, Any]] = Column(JSON, nullable=False, default=list)
    
    # Diagnostic mode: "with_memory" or "without_memory"
    mode: str = Column(String(16), nullable=False, default="with_memory")

    # Structured diagnostic trace from current evidence -> recall -> reasoning
    diagnostic_trace: Optional[Dict[str, Any]] = Column(JSON, nullable=True, default=dict)
    
    created_at: datetime = Column(DateTime, default=utcnow, nullable=False)

    # Relationships
    incident = relationship("Incident", back_populates="analyses")



class Runbook(Base):
    """Standard Operating Procedure (SOP) documentation for services."""

    __tablename__ = "runbooks"

    id: str = Column(String(32), primary_key=True)
    service: str = Column(String(64), nullable=False, index=True)
    title: str = Column(String(255), nullable=False)
    trigger_symptoms: List[str] = Column(JSON, nullable=False, default=list)
    standard_operating_procedure: str = Column(Text, nullable=False)
