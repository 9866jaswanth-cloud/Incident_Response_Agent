"""Pydantic schemas for Hindsight Memory status, timeline, and exploration."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MemoryStatusResponse(BaseModel):
    connected: bool = Field(..., description="Whether real Hindsight server is reachable")
    hindsight_base_url: str = Field(..., description="Configured Hindsight server URL")
    bank_id: str = Field(..., description="Active Hindsight memory bank")
    version: Optional[str] = Field(None, description="Hindsight server version if available")
    mode: str = Field(..., description="'REAL_HINDSIGHT' or 'OFFLINE_DEVELOPMENT_MODE'")
    message: str = Field(..., description="Status summary or setup instructions")


class MemoryTimelineEvent(BaseModel):
    id: int
    operation: str  # RETAIN, RECALL, REFLECT
    incident_id: Optional[str] = None
    bank_id: str
    query_or_content: str
    results_summary: str
    status: str
    duration_ms: float
    timestamp: datetime


class MemoryRecallPreviewRequest(BaseModel):
    query: str = Field(..., description="Text query to test recall against Hindsight memory bank")
    budget: str = Field("mid", description="Recall depth/budget: 'low', 'mid', 'high'")


class MemoryRecallPreviewResponse(BaseModel):
    query: str
    bank_id: str
    recalled_items: List[Dict[str, Any]]
    mode: str
