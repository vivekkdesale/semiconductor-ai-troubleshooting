from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RunSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    source: str
    source_key: str
    observed_at: datetime
    outcome: str
    feature_count: int
    missing_count: int


class InvestigationCreate(BaseModel):
    run_id: UUID | None = None
    summary: str = Field(min_length=3, max_length=5000)


class InvestigationView(InvestigationCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
