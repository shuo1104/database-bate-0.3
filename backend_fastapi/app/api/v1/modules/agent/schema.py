# -*- coding: utf-8 -*-
"""Agent ingest schemas for Phase 1."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AgentTaskStatus(str, Enum):
    pending = "pending"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


class AgentReviewStatus(str, Enum):
    pending_review = "pending_review"
    approved = "approved"
    rejected = "rejected"
    modified = "modified"


class AgentTaskSubmitResponse(BaseModel):
    task_id: int = Field(..., description="Task ID")
    task_type: str = Field(default="ingest", description="Task type")
    status: AgentTaskStatus = Field(..., description="Task status")
    file_name: str = Field(..., description="Original file name")
    file_path: str = Field(..., description="File storage path")
    created_at: datetime = Field(..., description="Task created time")


class AgentTaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: int = Field(..., alias="TaskID", description="Task ID")
    task_type: str = Field(..., alias="TaskType", description="Task type")
    status: AgentTaskStatus = Field(..., alias="Status", description="Task status")
    payload: dict[str, Any] | None = Field(
        default=None, alias="Payload", description="Task payload"
    )
    result: dict[str, Any] | None = Field(
        default=None, alias="Result", description="Task result"
    )
    error_message: str | None = Field(
        default=None, alias="ErrorMessage", description="Error message"
    )
    created_at: datetime = Field(..., alias="CreatedAt", description="Created at")
    started_at: datetime | None = Field(
        default=None, alias="StartedAt", description="Started at"
    )
    finished_at: datetime | None = Field(
        default=None, alias="FinishedAt", description="Finished at"
    )


class AgentReviewRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    record_id: int = Field(..., alias="RecordID", description="Ingestion record ID")
    task_id: int | None = Field(
        default=None, alias="TaskID_FK", description="Related task ID"
    )
    source_file_path: str = Field(
        ..., alias="SourceFilePath", description="Source file path"
    )
    source_file_name: str | None = Field(
        default=None, alias="SourceFileName", description="Source file name"
    )
    extracted_data: dict[str, Any] = Field(
        default_factory=dict,
        alias="ExtractedData",
        description="Structured extraction result",
    )
    field_confidences: dict[str, float] | None = Field(
        default=None, alias="FieldConfidences", description="Field confidence"
    )
    overall_confidence: float | None = Field(
        default=None, alias="OverallConfidence", description="Overall confidence"
    )
    review_status: AgentReviewStatus = Field(
        ..., alias="ReviewStatus", description="Review status"
    )
    reviewed_by_user_id: int | None = Field(
        default=None, alias="ReviewedByUserID_FK", description="Reviewer user ID"
    )
    reviewed_at: datetime | None = Field(
        default=None, alias="ReviewedAt", description="Reviewed at"
    )
    trace_meta: dict[str, Any] | None = Field(
        default=None, alias="TraceMeta", description="Trace metadata"
    )
    created_at: datetime = Field(..., alias="CreatedAt", description="Created at")


class AgentReviewListResponse(BaseModel):
    items: list[AgentReviewRecordResponse] = Field(
        default_factory=list, description="Review record list"
    )
    total: int = Field(..., ge=0, description="Total count")
    page: int = Field(..., ge=1, description="Page number")
    page_size: int = Field(..., ge=1, description="Page size")


class AgentReviewUpdateRequest(BaseModel):
    action: Literal["approved", "rejected", "modified"] = Field(
        ..., description="Review action"
    )
    modified_data: dict[str, Any] | None = Field(
        default=None, description="Manually modified structured data"
    )
    comment: str | None = Field(
        default=None, max_length=1000, description="Review comment"
    )


class AgentReviewUpdateResponse(BaseModel):
    record_id: int = Field(..., description="Record ID")
    review_status: AgentReviewStatus = Field(..., description="Review status")
    reviewed_by_user_id: int | None = Field(
        default=None, description="Reviewer user ID"
    )
    reviewed_at: datetime = Field(..., description="Reviewed at")
    task_id: int | None = Field(default=None, description="Related task ID")
    persist_result: dict[str, Any] | None = Field(
        default=None, description="Persistence result to business tables"
    )


class AgentReviewDeleteResponse(BaseModel):
    record_id: int = Field(..., description="Deleted record ID")
    task_id: int | None = Field(default=None, description="Related task ID")
    review_status: AgentReviewStatus = Field(
        ..., description="Review status before delete"
    )
    deleted_at: datetime = Field(..., description="Delete timestamp")


class AgentChatIntent(str, Enum):
    ingest = "ingest"
    query = "query"
    mutate_domain = "mutate_domain"
    mutate_bulk = "mutate_bulk"
    admin_ops = "admin_ops"
    clarify = "clarify"
    general = "general"


class AgentChatMode(str, Enum):
    sync = "sync"
    async_task = "async_task"
    follow_up = "follow_up"


class AgentPlanApprovalStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class AgentToolTrace(BaseModel):
    tool_name: str = Field(..., description="Tool name")
    status: Literal["ok", "failed", "skipped"] = Field(
        default="ok",
        description="Tool execution status",
    )
    tool_input: dict[str, Any] | None = Field(
        default=None, description="Tool input summary"
    )
    tool_output: dict[str, Any] | None = Field(
        default=None, description="Tool output summary"
    )
    error: str | None = Field(default=None, description="Error message")
    duration_ms: int | None = Field(
        default=None, ge=0, description="Tool duration (ms)"
    )


class AgentChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000, description="User input")
    project_scope: list[int] | None = Field(
        default=None,
        description="Accessible project ID scope for user",
    )
    top_k: int = Field(default=100, ge=1, le=1000, description="Maximum query rows")

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("message cannot be empty")
        return stripped


class AgentChatResponse(BaseModel):
    mode: AgentChatMode = Field(..., description="Response mode")
    intent: AgentChatIntent = Field(..., description="Detected intent")
    reply: str = Field(..., description="Text reply to user")
    follow_up_question: str | None = Field(
        default=None,
        description="Follow-up question when information is insufficient",
    )
    task_id: int | None = Field(default=None, description="Async task ID")
    query_result: dict[str, Any] | None = Field(
        default=None,
        description="Query result summary",
    )
    tool_traces: list[AgentToolTrace] = Field(
        default_factory=list,
        description="Tool execution traces",
    )
    degraded: bool = Field(default=False, description="Whether degraded")
    retryable: bool = Field(default=False, description="Whether error is retryable")
    audit_id: int | None = Field(default=None, description="Audit log ID")


class AgentChangePlanApprovalRequest(BaseModel):
    action: Literal["approve", "reject"] = Field(..., description="Approval action")
    comment: str | None = Field(
        default=None, max_length=1000, description="Approval comment"
    )


class AgentChangePlanApprovalResponse(BaseModel):
    task_id: int = Field(..., description="Plan task ID")
    approval_status: AgentPlanApprovalStatus = Field(..., description="Approval status")
    approved_by_user_id: int | None = Field(
        default=None, description="Approver user ID"
    )
    approved_by_role: str | None = Field(default=None, description="Approver role")
    approved_at: datetime | None = Field(default=None, description="Approved at")
    comment: str | None = Field(default=None, description="Approval comment")


class AgentChangePlanRecordResponse(BaseModel):
    task_id: int = Field(..., description="Plan task ID")
    task_status: AgentTaskStatus = Field(..., description="Task status")
    approval_status: AgentPlanApprovalStatus = Field(..., description="Approval status")
    created_by_user_id: int | None = Field(default=None, description="Creator user ID")
    created_by_role: str | None = Field(default=None, description="Creator role")
    approved_by_user_id: int | None = Field(
        default=None, description="Approver user ID"
    )
    approved_by_role: str | None = Field(default=None, description="Approver role")
    executed_by_user_id: int | None = Field(
        default=None, description="Executor user ID"
    )
    executed_by_role: str | None = Field(default=None, description="Executor role")
    created_at: datetime = Field(..., description="Created at")
    approved_at: datetime | None = Field(default=None, description="Approved at")
    executed_at: datetime | None = Field(default=None, description="Executed at")
    plan_summary: str | None = Field(default=None, description="Plan summary")
    plan: dict[str, Any] | None = Field(
        default=None, description="Structured change plan"
    )
    preview_result: dict[str, Any] | None = Field(
        default=None,
        description="Pre-execution preview (estimated affected rows)",
    )
    rollback_snapshot: dict[str, Any] | None = Field(
        default=None,
        description="Pre-execution rollback snapshot",
    )
    execution_result: dict[str, Any] | None = Field(
        default=None,
        description="Execution result",
    )
    error_message: str | None = Field(default=None, description="Error message")


class AgentChangePlanListResponse(BaseModel):
    items: list[AgentChangePlanRecordResponse] = Field(
        default_factory=list,
        description="Plan approval list",
    )
    total: int = Field(..., ge=0, description="Total count")
    page: int = Field(..., ge=1, description="Page number")
    page_size: int = Field(..., ge=1, description="Page size")


class AgentChangePlanExecutionResponse(BaseModel):
    task_id: int = Field(..., description="Plan task ID")
    status: AgentTaskStatus = Field(..., description="Task status after execution")
    executed_by_user_id: int | None = Field(
        default=None, description="Executor user ID"
    )
    executed_by_role: str | None = Field(default=None, description="Executor role")
    executed_at: datetime | None = Field(default=None, description="Executed at")
    execution_result: dict[str, Any] | None = Field(
        default=None, description="Execution result"
    )
    rollback_performed: bool = Field(
        default=False,
        description="Whether compensating rollback was performed after failure",
    )
