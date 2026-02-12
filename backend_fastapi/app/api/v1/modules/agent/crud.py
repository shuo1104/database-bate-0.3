# -*- coding: utf-8 -*-
"""Agent CRUD operations."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.modules.agent.model import (
    AgentAuditLogModel,
    AgentIngestRecordModel,
    AgentTaskModel,
)


class AgentCRUD:
    """Data access for Phase 1 ingest flow."""

    @staticmethod
    async def create_task(
        db: AsyncSession,
        task_type: str,
        status: str,
        payload: dict[str, Any] | None = None,
    ) -> AgentTaskModel:
        task = AgentTaskModel(
            TaskType=task_type,
            Status=status,
            Payload=payload,
        )
        db.add(task)
        await db.flush()
        return task

    @staticmethod
    async def get_task_by_id(db: AsyncSession, task_id: int) -> AgentTaskModel | None:
        stmt = select(AgentTaskModel).where(AgentTaskModel.TaskID == task_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_tasks_paginated(
        db: AsyncSession,
        *,
        page: int,
        page_size: int,
        task_type: str | None = None,
        status: str | None = None,
    ) -> tuple[list[AgentTaskModel], int]:
        conditions = []
        if task_type:
            conditions.append(AgentTaskModel.TaskType == task_type)
        if status:
            conditions.append(AgentTaskModel.Status == status)

        count_stmt = select(func.count()).select_from(AgentTaskModel)
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))
        total_result = await db.execute(count_stmt)
        total = int(total_result.scalar() or 0)

        stmt = select(AgentTaskModel)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(AgentTaskModel.CreatedAt.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(stmt)
        return list(result.scalars().all()), total

    @staticmethod
    async def get_tasks_by_type(
        db: AsyncSession,
        *,
        task_type: str,
        status: str | None = None,
    ) -> list[AgentTaskModel]:
        stmt = select(AgentTaskModel).where(AgentTaskModel.TaskType == task_type)
        if status:
            stmt = stmt.where(AgentTaskModel.Status == status)
        stmt = stmt.order_by(AgentTaskModel.CreatedAt.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def update_task(
        db: AsyncSession,
        task: AgentTaskModel,
        *,
        status: str | None = None,
        payload: dict[str, Any] | None = None,
        result: dict[str, Any] | None = None,
        error_message: str | None = None,
        started_at: datetime | None = None,
        finished_at: datetime | None = None,
    ) -> AgentTaskModel:
        if status is not None:
            task.Status = status
        if payload is not None:
            task.Payload = payload
        if result is not None:
            task.Result = result
        if error_message is not None:
            task.ErrorMessage = error_message
        if started_at is not None:
            task.StartedAt = started_at
        if finished_at is not None:
            task.FinishedAt = finished_at
        await db.flush()
        return task

    @staticmethod
    async def create_ingest_record(
        db: AsyncSession,
        *,
        task_id: int,
        source_file_path: str,
        source_file_name: str,
        extracted_data: dict[str, Any],
        field_confidences: dict[str, float],
        overall_confidence: float,
        review_status: str,
        trace_meta: dict[str, Any] | None = None,
    ) -> AgentIngestRecordModel:
        record = AgentIngestRecordModel(
            TaskID_FK=task_id,
            SourceFilePath=source_file_path,
            SourceFileName=source_file_name,
            ExtractedData=extracted_data,
            FieldConfidences=field_confidences,
            OverallConfidence=overall_confidence,
            ReviewStatus=review_status,
            TraceMeta=trace_meta,
        )
        db.add(record)
        await db.flush()
        return record

    @staticmethod
    async def get_ingest_record_by_id(
        db: AsyncSession, record_id: int
    ) -> AgentIngestRecordModel | None:
        stmt = select(AgentIngestRecordModel).where(
            AgentIngestRecordModel.RecordID == record_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_review_records_paginated(
        db: AsyncSession,
        *,
        page: int,
        page_size: int,
        review_status: str | None = None,
        task_id: int | None = None,
        file_type: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> tuple[list[AgentIngestRecordModel], int]:
        conditions = []

        if review_status == "pending_review":
            conditions.append(AgentIngestRecordModel.ReviewedByUserID_FK.is_(None))
        elif review_status:
            conditions.append(AgentIngestRecordModel.ReviewStatus == review_status)
        if task_id is not None:
            conditions.append(AgentIngestRecordModel.TaskID_FK == task_id)
        if file_type:
            normalized = file_type.lower().lstrip(".")
            conditions.append(
                func.lower(AgentIngestRecordModel.SourceFileName).like(
                    f"%.{normalized}"
                )
            )
        if start_time:
            conditions.append(AgentIngestRecordModel.CreatedAt >= start_time)
        if end_time:
            conditions.append(AgentIngestRecordModel.CreatedAt <= end_time)

        count_stmt = select(func.count()).select_from(AgentIngestRecordModel)
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))
        total_result = await db.execute(count_stmt)
        total = int(total_result.scalar() or 0)

        stmt = select(AgentIngestRecordModel)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(AgentIngestRecordModel.CreatedAt.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(stmt)
        return list(result.scalars().all()), total

    @staticmethod
    async def update_ingest_review(
        db: AsyncSession,
        record: AgentIngestRecordModel,
        *,
        review_status: str,
        reviewed_by_user_id: int,
        reviewed_at: datetime,
        modified_data: dict[str, Any] | None = None,
    ) -> AgentIngestRecordModel:
        record.ReviewStatus = review_status
        record.ReviewedByUserID_FK = reviewed_by_user_id
        record.ReviewedAt = reviewed_at
        if modified_data is not None:
            record.ExtractedData = modified_data
        await db.flush()
        return record

    @staticmethod
    async def append_audit_log(
        db: AsyncSession,
        *,
        user_id: int | None,
        task_id: int | None,
        action_type: str,
        user_input: dict[str, Any] | None = None,
        tool_trace: dict[str, Any] | None = None,
        final_response: str | None = None,
        duration_ms: int | None = None,
    ) -> AgentAuditLogModel:
        audit_log = AgentAuditLogModel(
            UserID_FK=user_id,
            TaskID_FK=task_id,
            ActionType=action_type,
            UserInput=user_input,
            ToolTrace=tool_trace,
            FinalResponse=final_response,
            DurationMs=duration_ms,
        )
        db.add(audit_log)
        await db.flush()
        return audit_log
