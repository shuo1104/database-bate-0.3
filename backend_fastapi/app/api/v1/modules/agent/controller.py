# -*- coding: utf-8 -*-
"""Agent API endpoints (ingest/review/chat)."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.modules.agent.schema import (
    AgentChatRequest,
    AgentChangePlanApprovalResponse,
    AgentChangePlanApprovalRequest,
    AgentChangePlanExecutionResponse,
    AgentChangePlanListResponse,
    AgentPlanApprovalStatus,
    AgentReviewDeleteResponse,
    AgentReviewStatus,
    AgentReviewUpdateRequest,
    AgentTaskStatus,
)
from app.api.v1.modules.agent.db_admin import AgentDbAdminService
from app.api.v1.modules.agent.service import AgentChatService, AgentIngestService
from app.common.response import ResponseModel, SuccessResponse
from app.core.database import get_db
from app.core.custom_exceptions import ValidationException
from app.core.logger import logger
from app.core.security import get_current_user_info

router = APIRouter()


def _encode_ndjson_event(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8")


def _iter_text_chunks(text: str, *, chunk_size: int = 12) -> list[str]:
    normalized = (text or "").strip()
    if not normalized:
        return []

    return [
        normalized[start : start + chunk_size]
        for start in range(0, len(normalized), chunk_size)
    ]


def _parse_project_scope(scope_text: str | None) -> list[int] | None:
    if scope_text is None:
        return None

    normalized = scope_text.strip()
    if not normalized:
        return None

    try:
        decoded = json.loads(normalized)
        if isinstance(decoded, list):
            return [int(item) for item in decoded]
    except Exception:  # noqa: BLE001
        pass

    try:
        values = [
            int(chunk.strip()) for chunk in normalized.split(",") if chunk.strip()
        ]
    except ValueError as exc:
        raise ValidationException(
            "project_scope must be JSON list or comma-separated integers"
        ) from exc

    return values or None


@router.post(
    "/ingest",
    response_model=None,
    summary="Submit document ingestion task",
    description="Upload PDF/image/CSV and create an asynchronous ingestion task",
)
async def submit_ingest_task(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="File to ingest"),
    current_user: dict = Depends(get_current_user_info),
    db: AsyncSession = Depends(get_db),
):
    result = await AgentIngestService.submit_ingest_task(
        db=db,
        background_tasks=background_tasks,
        file=file,
        user_id=int(current_user["user_id"]),
        user_role=str(current_user.get("role") or "user"),
    )
    return SuccessResponse(
        data=result.model_dump(mode="json"), msg="Task submitted successfully"
    )


@router.get(
    "/tasks/{task_id}",
    response_model=None,
    summary="Query task status",
    description="Query asynchronous ingestion task status and result by task ID",
)
async def get_task_status(
    task_id: int,
    current_user: dict = Depends(get_current_user_info),
    db: AsyncSession = Depends(get_db),
):
    result = await AgentIngestService.get_task_status(
        db=db,
        task_id=task_id,
        user_role=str(current_user.get("role") or "user"),
    )
    return SuccessResponse(data=result.model_dump(mode="json"), msg="Query succeeded")


@router.get(
    "/review",
    response_model=None,
    summary="Get ingestion records for review",
    description="Paginated query of ingestion records (default: all statuses)",
)
async def get_review_records(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    review_status: AgentReviewStatus | None = Query(
        None,
        description="Review status",
    ),
    task_id: int | None = Query(None, ge=1, description="Filter by task ID"),
    file_type: str | None = Query(
        None, description="Filter by file type (pdf/csv/png...)"
    ),
    start_time: datetime | None = Query(None, description="Start time"),
    end_time: datetime | None = Query(None, description="End time"),
    current_user: dict = Depends(get_current_user_info),
    db: AsyncSession = Depends(get_db),
):
    result = await AgentIngestService.list_review_records(
        db=db,
        page=page,
        page_size=page_size,
        review_status=review_status.value if review_status else None,
        task_id=task_id,
        file_type=file_type,
        start_time=start_time,
        end_time=end_time,
        reviewer_role=str(current_user.get("role") or "user"),
    )
    return SuccessResponse(data=result.model_dump(mode="json"), msg="Query succeeded")


@router.put(
    "/review/{record_id}",
    response_model=None,
    summary="Review ingestion record",
    description="Approve/reject/modify an ingestion record",
)
async def review_ingest_record(
    record_id: int,
    review_data: AgentReviewUpdateRequest,
    current_user: dict = Depends(get_current_user_info),
    db: AsyncSession = Depends(get_db),
):
    result = await AgentIngestService.review_record(
        db=db,
        record_id=record_id,
        review_data=review_data,
        reviewer_user_id=int(current_user["user_id"]),
        reviewer_role=str(current_user.get("role") or "user"),
    )
    return SuccessResponse(data=result.model_dump(mode="json"), msg="Review completed")


@router.delete(
    "/review/{record_id}",
    response_model=ResponseModel[AgentReviewDeleteResponse],
    summary="Delete ingestion review record",
    description="Delete one ingestion review record by record ID",
)
async def delete_review_record(
    record_id: int,
    current_user: dict = Depends(get_current_user_info),
    db: AsyncSession = Depends(get_db),
):
    result = await AgentIngestService.delete_review_record(
        db=db,
        record_id=record_id,
        reviewer_user_id=int(current_user["user_id"]),
        reviewer_role=str(current_user.get("role") or "user"),
    )
    return SuccessResponse(data=result.model_dump(mode="json"), msg="Record deleted")


@router.get(
    "/plans",
    response_model=ResponseModel[AgentChangePlanListResponse],
    summary="Get database change plan approval list",
    description="Paginated query for db_change_plan tasks with creator/approver/executor and preview snapshot",
)
async def list_change_plans(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    task_status: AgentTaskStatus | None = Query(
        None, description="Filter by task status"
    ),
    approval_status: AgentPlanApprovalStatus | None = Query(
        None,
        description="Filter by approval status",
    ),
    current_user: dict = Depends(get_current_user_info),
    db: AsyncSession = Depends(get_db),
):
    AgentIngestService._ensure_agent_role(str(current_user.get("role") or "user"))
    result = await AgentDbAdminService.list_change_plan_tasks(
        db,
        page=page,
        page_size=page_size,
        task_status=task_status.value if task_status else None,
        approval_status=approval_status.value if approval_status else None,
    )
    return SuccessResponse(data=result, msg="Query succeeded")


@router.post(
    "/plans/{task_id}/approve",
    response_model=ResponseModel[AgentChangePlanApprovalResponse],
    summary="Approve database change plan",
    description="After approval, the plan can be executed; after rejection, the plan is terminated",
)
async def approve_change_plan(
    task_id: int,
    approval_data: AgentChangePlanApprovalRequest,
    current_user: dict = Depends(get_current_user_info),
    db: AsyncSession = Depends(get_db),
):
    result = await AgentDbAdminService.approve_change_plan_task(
        db,
        task_id=task_id,
        action=approval_data.action,
        approver_user_id=int(current_user["user_id"]),
        approver_role=str(current_user.get("role") or "user"),
        comment=approval_data.comment,
    )
    return SuccessResponse(data=result, msg="Approval completed")


@router.post(
    "/plans/{task_id}/execute",
    response_model=ResponseModel[AgentChangePlanExecutionResponse],
    summary="Execute database change plan",
    description="Only approved plans can be executed; on failure, snapshot rollback is attempted",
)
async def execute_change_plan(
    task_id: int,
    current_user: dict = Depends(get_current_user_info),
    db: AsyncSession = Depends(get_db),
):
    result = await AgentDbAdminService.execute_plan_task(
        db,
        task_id=task_id,
        user_id=int(current_user["user_id"]),
        user_role=str(current_user.get("role") or "user"),
    )
    return SuccessResponse(data=result, msg="Execution completed")


@router.post(
    "/chat",
    response_model=None,
    summary="Agent chat entry",
    description="Submit a text question (optional file) and let Agent route to query/ingestion capabilities",
)
async def chat_with_agent(
    background_tasks: BackgroundTasks,
    message: str = Form(..., description="User question"),
    top_k: int = Form(100, ge=1, le=1000, description="Maximum number of query rows"),
    project_scope: str | None = Form(
        None,
        description="Project permission scope, JSON array or comma-separated integers",
    ),
    file: UploadFile | None = File(
        None, description="Optional file (used for ingestion)"
    ),
    current_user: dict = Depends(get_current_user_info),
    db: AsyncSession = Depends(get_db),
):
    request = AgentChatRequest(
        message=message,
        project_scope=_parse_project_scope(project_scope),
        top_k=top_k,
    )
    result = await AgentChatService.handle_chat(
        db=db,
        background_tasks=background_tasks,
        request=request,
        current_user=current_user,
        file=file,
    )
    return SuccessResponse(
        data=result.model_dump(mode="json"), msg="Processed successfully"
    )


@router.post(
    "/chat/stream",
    response_model=None,
    summary="Agent chat streaming entry",
    description=(
        "Submit a text question (optional file) and stream response chunks as NDJSON"
    ),
)
async def chat_with_agent_stream(
    background_tasks: BackgroundTasks,
    message: str = Form(..., description="User question"),
    top_k: int = Form(100, ge=1, le=1000, description="Maximum number of query rows"),
    project_scope: str | None = Form(
        None,
        description="Project permission scope, JSON array or comma-separated integers",
    ),
    file: UploadFile | None = File(
        None, description="Optional file (used for ingestion)"
    ),
    current_user: dict = Depends(get_current_user_info),
    db: AsyncSession = Depends(get_db),
):
    request = AgentChatRequest(
        message=message,
        project_scope=_parse_project_scope(project_scope),
        top_k=top_k,
    )

    async def stream_events():
        yield _encode_ndjson_event({"type": "start"})

        try:
            result = await AgentChatService.handle_chat(
                db=db,
                background_tasks=background_tasks,
                request=request,
                current_user=current_user,
                file=file,
            )

            for chunk in _iter_text_chunks(result.reply):
                yield _encode_ndjson_event({"type": "delta", "content": chunk})
                await asyncio.sleep(0.02)

            yield _encode_ndjson_event(
                {
                    "type": "done",
                    "response": result.model_dump(mode="json"),
                }
            )
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Agent chat stream failed: %s: %s",
                type(exc).__name__,
                exc,
                exc_info=True,
            )
            yield _encode_ndjson_event(
                {
                    "type": "error",
                    "message": "Agent chat stream failed",
                }
            )

    return StreamingResponse(
        stream_events(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
