"""Schemas for document ingest outputs."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class IngestFieldConfidence(BaseModel):
    field: str = Field(..., description="Field name")
    score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    reason: str | None = Field(default=None, description="Confidence explanation")


class IngestOutputSchema(BaseModel):
    task_id: int | None = Field(default=None, description="Task ID")
    source_file_path: str = Field(..., description="Original file path")
    extracted_data: dict[str, Any] = Field(
        default_factory=dict, description="Structured extraction result"
    )
    field_confidences: list[IngestFieldConfidence] = Field(
        default_factory=list,
        description="Field confidence list",
    )
    overall_confidence: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Overall confidence"
    )
    review_status: str = Field(default="pending_review", description="Review status")
    created_at: datetime | None = Field(default=None, description="Created at")
