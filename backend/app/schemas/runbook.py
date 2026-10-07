"""Pydantic schemas for Runbooks / SOPs."""

from typing import List
from pydantic import BaseModel, ConfigDict


class RunbookResponse(BaseModel):
    id: str
    service: str
    title: str
    trigger_symptoms: List[str]
    standard_operating_procedure: str

    model_config = ConfigDict(from_attributes=True)
