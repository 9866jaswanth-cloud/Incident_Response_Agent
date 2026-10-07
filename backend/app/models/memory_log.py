"""Audit trail model for all Hindsight memory interactions."""

from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)
from app.core.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class MemoryAuditLog(Base):
    """Logs every retain, recall, and reflect operation against Hindsight."""

    __tablename__ = "memory_audit_logs"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    operation: str = Column(String(16), nullable=False, index=True)  # RETAIN, RECALL, REFLECT
    bank_id: str = Column(String(64), nullable=False)
    incident_id: str = Column(String(32), nullable=True, index=True)
    query_or_content: str = Column(Text, nullable=False)
    results_summary: str = Column(Text, nullable=False)
    status: str = Column(String(32), nullable=False, default="SUCCESS")  # SUCCESS, OFFLINE_FALLBACK, FAILED
    duration_ms: float = Column(Float, nullable=False, default=0.0)
    timestamp: datetime = Column(DateTime, default=utcnow, nullable=False, index=True)
