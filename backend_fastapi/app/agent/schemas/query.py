"""Schemas for text-to-SQL query requests and responses."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class QueryRequestSchema(BaseModel):
    question: str = Field(..., min_length=1, description="Natural language query")
    project_scope: list[int] | None = Field(
        default=None, description="Accessible project scope"
    )
    top_k: int = Field(default=100, ge=1, le=1000, description="Maximum returned rows")


class QueryResponseSchema(BaseModel):
    sql: str = Field(..., description="Generated and executed SQL")
    columns: list[str] = Field(default_factory=list, description="Result columns")
    rows: list[dict[str, Any]] = Field(default_factory=list, description="Result rows")
    row_count: int = Field(default=0, ge=0, description="Result row count")
    retries: int = Field(default=0, ge=0, description="Self-correction retry count")
    duration_ms: int = Field(default=0, ge=0, description="Query duration (ms)")
    formatted_text: str = Field(default="", description="Formatted text output")
    warning: str | None = Field(default=None, description="Warning message")
