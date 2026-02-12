# -*- coding: utf-8 -*-
"""Agent services for ingest/review/chat workflows."""

from __future__ import annotations

import asyncio
import csv
import hashlib
import json
import mimetypes
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from fastapi import BackgroundTasks, UploadFile
from sqlalchemy import select as sa_select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.config import (
    get_agent_authorization_config,
    get_deepseek_config,
    get_mineru_config,
)
from app.agent.core.audit_callback import AgentAuditCallbackHandler
from app.agent.core.llm import create_deepseek_client
from app.agent.core.request_context import (
    AgentRequestContext,
    reset_agent_request_context,
    set_agent_request_context,
)
from app.agent.core.react_agent import build_react_agent
from app.agent.schemas import QueryRequestSchema
from app.agent.tools.etl import agent_document_ingest
from app.agent.tools.sql import TextToSqlService
from app.api.v1.modules.agent.crud import AgentCRUD
from app.api.v1.modules.agent.db_admin import AgentDbAdminService
from app.api.v1.modules.agent.schema import (
    AgentChatIntent,
    AgentChatMode,
    AgentChatRequest,
    AgentChatResponse,
    AgentReviewListResponse,
    AgentReviewDeleteResponse,
    AgentReviewRecordResponse,
    AgentReviewStatus,
    AgentReviewUpdateRequest,
    AgentReviewUpdateResponse,
    AgentTaskResponse,
    AgentTaskStatus,
    AgentTaskSubmitResponse,
    AgentToolTrace,
)
from app.config.settings import settings
from app.core.custom_exceptions import (
    AuthorizationException,
    DatabaseException,
    ExternalServiceException,
    RecordNotFoundException,
    ValidationException,
)
from app.core.database import AsyncSessionLocal
from app.core.logger import logger


class AgentIngestService:
    """Business logic for Agent ingest endpoints."""

    @staticmethod
    def _ensure_agent_role(user_role: str) -> None:
        auth_cfg = get_agent_authorization_config()
        if not auth_cfg.can_use_agent(user_role):
            raise AuthorizationException("Current role is not allowed to use agent")

    @staticmethod
    def _ensure_review_role(user_role: str) -> None:
        auth_cfg = get_agent_authorization_config()
        if not auth_cfg.can_review(user_role):
            raise AuthorizationException(
                "Current role is not allowed to review ingest records"
            )

    @staticmethod
    def _ensure_mutation_role(user_role: str) -> None:
        auth_cfg = get_agent_authorization_config()
        if not auth_cfg.can_mutate(user_role):
            raise AuthorizationException(
                "Current role is not allowed to execute DB mutation operations"
            )

    @staticmethod
    def _ensure_admin_role(user_role: str) -> None:
        auth_cfg = get_agent_authorization_config()
        if not auth_cfg.can_admin(user_role):
            raise AuthorizationException(
                "Current role is not allowed to execute DB admin operations"
            )

    @staticmethod
    async def submit_ingest_task(
        db: AsyncSession,
        background_tasks: BackgroundTasks,
        file: UploadFile,
        user_id: int,
        user_role: str = "user",
    ) -> AgentTaskSubmitResponse:
        AgentIngestService._ensure_agent_role(user_role)

        if not file.filename:
            raise ValidationException("Uploaded file must include filename")

        extension = Path(file.filename).suffix.lower()
        if not extension:
            raise ValidationException("Uploaded file extension is missing")

        allowed_extensions = {
            ext.lower() for ext in (settings.AGENT_ALLOWED_EXTENSIONS or [])
        }
        if extension not in allowed_extensions:
            raise ValidationException(
                f"Unsupported file type: {extension}. Allowed: {sorted(allowed_extensions)}"
            )

        file_content = await file.read()
        if not file_content:
            raise ValidationException("Uploaded file is empty")
        if len(file_content) > settings.AGENT_MAX_FILE_SIZE:
            raise ValidationException(
                f"File too large ({len(file_content)} bytes), max={settings.AGENT_MAX_FILE_SIZE}"
            )

        task = await AgentCRUD.create_task(
            db,
            task_type="ingest",
            status=AgentTaskStatus.pending.value,
            payload={
                "source_file_name": file.filename,
                "content_type": file.content_type,
                "uploader_user_id": user_id,
            },
        )

        safe_name = AgentIngestService._sanitize_filename(file.filename)
        target_path = AgentIngestService._build_storage_path(
            task_id=task.TaskID,
            safe_filename=safe_name,
        )
        await asyncio.to_thread(
            target_path.parent.mkdir,
            parents=True,
            exist_ok=True,
        )
        await asyncio.to_thread(target_path.write_bytes, file_content)

        payload = dict(task.Payload or {})
        payload.update(
            {
                "source_file_name": file.filename,
                "source_file_path": str(target_path),
                "saved_file_name": target_path.name,
                "file_extension": extension,
                "size_bytes": len(file_content),
                "sha256": hashlib.sha256(file_content).hexdigest(),
                "uploaded_at": datetime.now().isoformat(),
            }
        )

        await AgentCRUD.update_task(db, task, payload=payload)
        await db.commit()
        await db.refresh(task)

        background_tasks.add_task(AgentIngestService.run_ingest_pipeline, task.TaskID)

        return AgentTaskSubmitResponse(
            task_id=task.TaskID,
            task_type=task.TaskType,
            status=AgentTaskStatus.pending,
            file_name=file.filename,
            file_path=str(target_path),
            created_at=task.CreatedAt,
        )

    @staticmethod
    async def get_task_status(
        db: AsyncSession,
        task_id: int,
        user_role: str = "user",
    ) -> AgentTaskResponse:
        AgentIngestService._ensure_agent_role(user_role)

        task = await AgentCRUD.get_task_by_id(db, task_id)
        if not task:
            raise RecordNotFoundException("AgentTask", task_id)

        task.Status = AgentIngestService._normalize_task_status(task.Status)
        return AgentTaskResponse.model_validate(task)

    @staticmethod
    async def list_review_records(
        db: AsyncSession,
        *,
        page: int,
        page_size: int,
        review_status: str | None,
        task_id: int | None,
        file_type: str | None,
        start_time: datetime | None,
        end_time: datetime | None,
        reviewer_role: str,
    ) -> AgentReviewListResponse:
        AgentIngestService._ensure_review_role(reviewer_role)

        records, total = await AgentCRUD.get_review_records_paginated(
            db,
            page=page,
            page_size=page_size,
            review_status=review_status,
            task_id=task_id,
            file_type=file_type,
            start_time=start_time,
            end_time=end_time,
        )
        return AgentReviewListResponse(
            items=[AgentReviewRecordResponse.model_validate(item) for item in records],
            total=total,
            page=page,
            page_size=page_size,
        )

    @staticmethod
    async def review_record(
        db: AsyncSession,
        *,
        record_id: int,
        review_data: AgentReviewUpdateRequest,
        reviewer_user_id: int,
        reviewer_role: str,
    ) -> AgentReviewUpdateResponse:
        AgentIngestService._ensure_review_role(reviewer_role)

        record = await AgentCRUD.get_ingest_record_by_id(db, record_id)
        if not record:
            raise RecordNotFoundException("AgentIngestRecord", record_id)

        if record.ReviewedByUserID_FK is not None:
            raise ValidationException("This record has already been reviewed")

        if review_data.action == "modified" and not review_data.modified_data:
            raise ValidationException("modified_data is required when action=modified")

        reviewed_at = datetime.now()
        review_status = AgentReviewStatus(review_data.action).value

        updated_record = await AgentCRUD.update_ingest_review(
            db,
            record,
            review_status=review_status,
            reviewed_by_user_id=reviewer_user_id,
            reviewed_at=reviewed_at,
            modified_data=review_data.modified_data,
        )

        # ── Persist to domain tables on approval / modification ────
        persist_result: dict[str, Any] | None = None
        if review_status in (
            AgentReviewStatus.approved.value,
            AgentReviewStatus.modified.value,
        ):
            data_to_persist = dict(updated_record.ExtractedData or {})
            persist_result = await AgentIngestService._persist_to_domain_tables(
                db, data_to_persist
            )
            logger.info(
                "Domain persistence for record %s: %s", record_id, persist_result
            )

        # ── Update associated task ────────────────────────────────
        if updated_record.TaskID_FK:
            task = await AgentCRUD.get_task_by_id(db, updated_record.TaskID_FK)
            if task:
                normalized_status = AgentIngestService._normalize_task_status(
                    task.Status
                )
                task_result = dict(task.Result or {})
                task_result.update(
                    {
                        "review_status": review_status,
                        "review_comment": review_data.comment,
                        "reviewed_by_user_id": reviewer_user_id,
                        "reviewed_at": reviewed_at.isoformat(),
                        "persist_result": persist_result,
                    }
                )
                await AgentCRUD.update_task(
                    db,
                    task,
                    status=normalized_status,
                    result=task_result,
                )

        # ── Audit log ─────────────────────────────────────────────
        await AgentCRUD.append_audit_log(
            db,
            user_id=reviewer_user_id,
            task_id=updated_record.TaskID_FK,
            action_type="ingest_record_reviewed",
            user_input={
                "record_id": record_id,
                "action": review_data.action,
            },
            tool_trace={
                "comment": review_data.comment,
                "review_status": review_status,
                "modified_data_keys": sorted((review_data.modified_data or {}).keys()),
                "persist_result": persist_result,
            },
        )

        await db.commit()
        await db.refresh(updated_record)

        return AgentReviewUpdateResponse(
            record_id=updated_record.RecordID,
            review_status=AgentReviewStatus(updated_record.ReviewStatus),
            reviewed_by_user_id=updated_record.ReviewedByUserID_FK,
            reviewed_at=updated_record.ReviewedAt or reviewed_at,
            task_id=updated_record.TaskID_FK,
            persist_result=persist_result,
        )

    @staticmethod
    async def delete_review_record(
        db: AsyncSession,
        *,
        record_id: int,
        reviewer_user_id: int,
        reviewer_role: str,
    ) -> AgentReviewDeleteResponse:
        AgentIngestService._ensure_review_role(reviewer_role)

        record = await AgentCRUD.get_ingest_record_by_id(db, record_id)
        if not record:
            raise RecordNotFoundException("AgentIngestRecord", record_id)

        task_id = record.TaskID_FK
        original_status = AgentReviewStatus(record.ReviewStatus)
        deleted_at = datetime.now()

        await AgentCRUD.delete_ingest_record(db, record)

        await AgentCRUD.append_audit_log(
            db,
            user_id=reviewer_user_id,
            task_id=task_id,
            action_type="ingest_record_deleted",
            user_input={"record_id": record_id},
            tool_trace={
                "record_id": record_id,
                "task_id": task_id,
                "previous_review_status": original_status.value,
            },
        )

        await db.commit()

        return AgentReviewDeleteResponse(
            record_id=record_id,
            task_id=task_id,
            review_status=original_status,
            deleted_at=deleted_at,
        )

    @staticmethod
    async def run_ingest_pipeline(task_id: int) -> None:
        started_at = datetime.now()

        async with AsyncSessionLocal() as db:
            task = await AgentCRUD.get_task_by_id(db, task_id)
            if not task:
                logger.error("Agent task not found, task_id=%s", task_id)
                return

            try:
                await AgentCRUD.update_task(
                    db,
                    task,
                    status=AgentTaskStatus.running.value,
                    started_at=started_at,
                    error_message=None,
                )
                await db.commit()

                payload = dict(task.Payload or {})
                source_file_path = payload.get("source_file_path")
                source_file_name = payload.get("source_file_name") or ""

                if not source_file_path:
                    raise ValidationException("Task payload missing source_file_path")

                mineru_output = await AgentIngestService.parse_document_with_mineru(
                    source_file_path,
                    source_file_name,
                )

                # If MinerU completely failed (fallback with no content),
                # mark task as failed instead of creating an empty review record
                is_fallback = mineru_output.get("source") == "fallback"
                has_content = bool(
                    (mineru_output.get("raw_text") or "").strip()
                    or (mineru_output.get("structured_content") or {}).get(
                        "content_list"
                    )
                )
                if is_fallback and not has_content:
                    fallback_warning = mineru_output.get("warning", "OCR unavailable")
                    raise ExternalServiceException(
                        "MinerU",
                        f"OCR processing failed, no content extracted: {fallback_warning}",
                    )

                structured_data = await AgentIngestService.extract_structured_data(
                    mineru_output
                )
                validation_result = AgentIngestService.validate_and_score_data(
                    structured_data
                )

                overall_confidence = validation_result["overall_confidence"]
                review_status = (
                    AgentReviewStatus.pending_review.value
                    if overall_confidence < settings.AGENT_REVIEW_CONFIDENCE_THRESHOLD
                    else AgentReviewStatus.approved.value
                )

                trace_meta = {
                    "mineru_source": mineru_output.get("source"),
                    "ingest_at": datetime.now().isoformat(),
                    "threshold": settings.AGENT_REVIEW_CONFIDENCE_THRESHOLD,
                    "validation_notes": validation_result["validation_notes"],
                }

                record = await AgentCRUD.create_ingest_record(
                    db,
                    task_id=task.TaskID,
                    source_file_path=source_file_path,
                    source_file_name=source_file_name,
                    extracted_data=validation_result["extracted_data"],
                    field_confidences=validation_result["field_confidences"],
                    overall_confidence=overall_confidence,
                    review_status=review_status,
                    trace_meta=trace_meta,
                )

                persisted_summary = (
                    await AgentIngestService.auto_persist_validated_data(
                        db,
                        validation_result["extracted_data"],
                        review_status,
                    )
                )

                duration_ms = int((datetime.now() - started_at).total_seconds() * 1000)
                result_payload = {
                    "task_id": task.TaskID,
                    "record_id": record.RecordID,
                    "review_status": review_status,
                    "overall_confidence": overall_confidence,
                    "field_confidences": validation_result["field_confidences"],
                    "persisted_summary": persisted_summary,
                }

                await AgentCRUD.append_audit_log(
                    db,
                    user_id=payload.get("uploader_user_id"),
                    task_id=task.TaskID,
                    action_type="ingest_completed",
                    user_input={
                        "source_file_name": source_file_name,
                    },
                    tool_trace={
                        "mineru_source": mineru_output.get("source"),
                        "record_id": record.RecordID,
                        "review_status": review_status,
                    },
                    final_response=json.dumps(result_payload, ensure_ascii=False),
                    duration_ms=duration_ms,
                )

                await AgentCRUD.update_task(
                    db,
                    task,
                    status=AgentTaskStatus.succeeded.value,
                    result=result_payload,
                    finished_at=datetime.now(),
                )
                await db.commit()
            except Exception as exc:  # noqa: BLE001
                await db.rollback()
                logger.error(
                    "Agent ingest pipeline failed, task_id=%s, error=%s: %s",
                    task_id,
                    type(exc).__name__,
                    exc,
                    exc_info=True,
                )

                failed_task = await AgentCRUD.get_task_by_id(db, task_id)
                if failed_task:
                    try:
                        await AgentCRUD.update_task(
                            db,
                            failed_task,
                            status=AgentTaskStatus.failed.value,
                            error_message=f"{type(exc).__name__}: {exc}",
                            finished_at=datetime.now(),
                        )
                        await AgentCRUD.append_audit_log(
                            db,
                            user_id=(failed_task.Payload or {}).get("uploader_user_id"),
                            task_id=failed_task.TaskID,
                            action_type="ingest_failed",
                            user_input={
                                "source_file_name": (failed_task.Payload or {}).get(
                                    "source_file_name"
                                )
                            },
                            tool_trace={
                                "error": f"{type(exc).__name__}: {exc}",
                            },
                        )
                        await db.commit()
                    except Exception:  # noqa: BLE001
                        await db.rollback()
                        logger.error(
                            "Failed to persist ingest failure state for task_id=%s",
                            task_id,
                            exc_info=True,
                        )

    @staticmethod
    async def parse_document_with_mineru(
        file_path: str,
        source_file_name: str,
    ) -> dict[str, Any]:
        extension = Path(source_file_name or file_path).suffix.lower()
        if extension == ".csv":
            return await AgentIngestService._parse_csv_locally(file_path)

        try:
            return await AgentIngestService._call_mineru_api(
                file_path, source_file_name
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "MinerU call failed, fallback enabled: %s: %s",
                type(exc).__name__,
                exc,
            )
            return AgentIngestService._build_fallback_parse_result(
                file_path,
                source_file_name,
                warning=f"MinerU unavailable: {type(exc).__name__}",
            )

    @staticmethod
    async def extract_structured_data(mineru_output: dict[str, Any]) -> dict[str, Any]:
        if mineru_output.get("source") == "csv_local":
            csv_structured = AgentIngestService._build_structured_data_from_csv(
                mineru_output
            )
            if csv_structured is not None:
                return csv_structured

        cfg = get_deepseek_config()
        if not cfg.api_key:
            return AgentIngestService._fallback_structured_data(mineru_output)

        try:
            raw_output = await AgentIngestService._call_deepseek_structuring(
                mineru_output
            )
            parsed = AgentIngestService._safe_parse_json(raw_output)
            if parsed is None:
                fallback = AgentIngestService._fallback_structured_data(mineru_output)
                fallback["llm_raw_output"] = raw_output
                return fallback
            return parsed
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Deepseek structuring failed, fallback enabled: %s: %s",
                type(exc).__name__,
                exc,
            )
            return AgentIngestService._fallback_structured_data(mineru_output)

    @staticmethod
    def validate_and_score_data(structured_data: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(structured_data, dict):
            structured_data = {"raw": structured_data}

        field_confidences: dict[str, float] = {}
        validation_notes: list[str] = []
        non_empty_fields = 0

        for key, value in structured_data.items():
            if value in (None, "", [], {}):
                score = 0.35
            elif isinstance(value, (dict, list)):
                score = 0.78
                non_empty_fields += 1
            else:
                score = 0.86
                non_empty_fields += 1
            field_confidences[key] = round(score, 4)

        if not structured_data:
            validation_notes.append("No structured fields were generated")
        elif non_empty_fields == 0:
            validation_notes.append("All structured fields are empty")

        if field_confidences:
            overall_confidence = round(
                sum(field_confidences.values()) / len(field_confidences), 4
            )
        else:
            overall_confidence = 0.0

        return {
            "extracted_data": structured_data,
            "field_confidences": field_confidences,
            "overall_confidence": overall_confidence,
            "validation_notes": validation_notes,
        }

    @staticmethod
    async def auto_persist_validated_data(
        db: AsyncSession,
        extracted_data: dict[str, Any],
        review_status: str,
    ) -> dict[str, Any]:
        """Auto-persist high-confidence data to domain tables during ingest."""
        if review_status != AgentReviewStatus.approved.value:
            return {
                "auto_persisted": False,
                "note": "Data stored in ingest record, awaiting manual review",
            }

        result = await AgentIngestService._persist_to_domain_tables(db, extracted_data)
        result["auto_persisted"] = True
        return result

    # ── Domain-table persistence engine (approved -> persist to business tables) ──────

    @staticmethod
    async def _persist_to_domain_tables(
        db: AsyncSession,
        extracted_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Dispatch validated data to the appropriate domain table(s).

        Reads ``target_table`` and ``domain_data`` from *extracted_data* and
        delegates to the corresponding ``_persist_*`` helper.  Returns a
        summary dict describing what was created (or why nothing was).
        """
        target = str(extracted_data.get("target_table", "unknown")).strip().lower()
        domain_data = extracted_data.get("domain_data")

        if not domain_data or target == "unknown":
            return {
                "persisted": False,
                "reason": "No domain target identified (target_table missing or 'unknown')",
            }

        try:
            if target == "raw_materials":
                return await AgentIngestService._persist_raw_materials(db, domain_data)
            if target == "fillers":
                return await AgentIngestService._persist_fillers(db, domain_data)
            if target == "project":
                return await AgentIngestService._persist_project(db, domain_data)
            if target == "formula_composition":
                return await AgentIngestService._persist_formula_compositions(
                    db, domain_data
                )
            if target.startswith("test_results_"):
                return await AgentIngestService._persist_test_result(
                    db, target, domain_data
                )
            return {
                "persisted": False,
                "reason": f"Unrecognized target_table: {target}",
            }
        except Exception as exc:
            logger.error(
                "Domain persistence failed for target=%s: %s",
                target,
                exc,
                exc_info=True,
            )
            return {
                "persisted": False,
                "target_table": target,
                "error": f"{type(exc).__name__}: {exc}",
            }

    # ── raw_materials ─────────────────────────────────────────────────

    @staticmethod
    async def _persist_raw_materials(
        db: AsyncSession,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        from app.api.v1.modules.materials.crud import MaterialCRUD
        from app.api.v1.modules.materials.model import MaterialModel

        items = data.get("items") if isinstance(data.get("items"), list) else [data]
        created_ids: list[int] = []
        skipped: list[str] = []

        for item in items:
            trade_name = str(item.get("TradeName") or "").strip()
            if not trade_name:
                skipped.append("missing TradeName")
                continue

            # Dedup: skip if material with same TradeName already exists
            dup = await db.execute(
                sa_select(MaterialModel).where(MaterialModel.TradeName == trade_name)
            )
            if dup.scalar_one_or_none():
                skipped.append(f"duplicate: {trade_name}")
                continue

            category_fk = None
            cat_name = str(item.get("CategoryName") or "").strip()
            if cat_name:
                category_fk = (
                    await AgentIngestService._find_or_create_material_category(
                        db, cat_name
                    )
                )

            material = await MaterialCRUD.create_material(
                db,
                trade_name=trade_name,
                category_fk=category_fk,
                supplier=str(item.get("Supplier") or "") or None,
                cas_number=str(item.get("CAS_Number") or "") or None,
                density=AgentIngestService._safe_float(item.get("Density")),
                viscosity=AgentIngestService._safe_float(item.get("Viscosity")),
                function_description=str(item.get("FunctionDescription") or "") or None,
            )
            created_ids.append(material.MaterialID)

        return {
            "persisted": bool(created_ids),
            "target_table": "tbl_RawMaterials",
            "created_ids": created_ids,
            "created_count": len(created_ids),
            "skipped": skipped,
        }

    # ── fillers ───────────────────────────────────────────────────────

    @staticmethod
    async def _persist_fillers(
        db: AsyncSession,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        from app.api.v1.modules.fillers.crud import FillerCRUD
        from app.api.v1.modules.fillers.model import FillerModel

        items = data.get("items") if isinstance(data.get("items"), list) else [data]
        created_ids: list[int] = []
        skipped: list[str] = []

        for item in items:
            trade_name = str(item.get("TradeName") or "").strip()
            if not trade_name:
                skipped.append("missing TradeName")
                continue

            dup = await db.execute(
                sa_select(FillerModel).where(FillerModel.TradeName == trade_name)
            )
            if dup.scalar_one_or_none():
                skipped.append(f"duplicate: {trade_name}")
                continue

            filler_type_fk = None
            type_name = str(item.get("FillerTypeName") or "").strip()
            if type_name:
                filler_type_fk = await AgentIngestService._find_or_create_filler_type(
                    db, type_name
                )

            filler = await FillerCRUD.create_filler(
                db,
                trade_name=trade_name,
                filler_type_fk=filler_type_fk,
                supplier=str(item.get("Supplier") or "") or None,
                particle_size=str(item.get("ParticleSize") or "") or None,
                is_silanized=AgentIngestService._safe_int(item.get("IsSilanized")),
                coupling_agent=str(item.get("CouplingAgent") or "") or None,
                surface_area=AgentIngestService._safe_float(item.get("SurfaceArea")),
            )
            created_ids.append(filler.FillerID)

        return {
            "persisted": bool(created_ids),
            "target_table": "tbl_InorganicFillers",
            "created_ids": created_ids,
            "created_count": len(created_ids),
            "skipped": skipped,
        }

    # ── project (+ optional compositions) ─────────────────────────────

    @staticmethod
    async def _persist_project(
        db: AsyncSession,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        from app.api.v1.modules.projects.crud import CompositionCRUD, ProjectCRUD
        from app.api.v1.modules.projects.model import ProjectModel

        items = data.get("items") if isinstance(data.get("items"), list) else [data]
        created_ids: list[int] = []
        project_names: list[str] = []
        formula_codes: list[str] = []
        skipped: list[str] = []
        compositions_created = 0

        for item in items:
            if not isinstance(item, dict):
                skipped.append("invalid row")
                continue

            project_name = str(item.get("ProjectName") or "").strip()
            if not project_name:
                skipped.append("missing ProjectName")
                continue

            dup = await db.execute(
                sa_select(ProjectModel).where(ProjectModel.ProjectName == project_name)
            )
            if dup.scalar_one_or_none():
                skipped.append(f"duplicate: {project_name}")
                continue

            type_name = (
                AgentIngestService._normalize_project_type_name(
                    str(item.get("ProjectTypeName") or "").strip()
                )
                or "Inkjet"
            )
            project_type_fk = await AgentIngestService._find_or_create_project_type(
                db, type_name
            )

            formulation_date = AgentIngestService._safe_date(
                item.get("FormulationDate")
            )
            if not formulation_date:
                formulation_date = datetime.now().date()

            formulator = str(item.get("FormulatorName") or "Agent").strip() or "Agent"

            project = await ProjectCRUD.create_project(
                db,
                project_name=project_name,
                project_type_fk=project_type_fk,
                formulator_name=formulator,
                formulation_date=formulation_date,
                substrate_application=str(item.get("SubstrateApplication") or "")
                or None,
            )

            created_ids.append(project.ProjectID)
            project_names.append(project_name)
            formula_codes.append(project.FormulaCode)

            compositions_raw = item.get("compositions") or []
            if isinstance(compositions_raw, list):
                for comp in compositions_raw:
                    if not isinstance(comp, dict):
                        continue
                    wp = AgentIngestService._safe_float(comp.get("WeightPercentage"))
                    if wp is None:
                        continue
                    mat_id = await AgentIngestService._resolve_material_name(
                        db,
                        comp.get("MaterialName") or comp.get("MaterialTradeName"),
                    )
                    fil_id = await AgentIngestService._resolve_filler_name(
                        db,
                        comp.get("FillerName") or comp.get("FillerTradeName"),
                    )
                    await CompositionCRUD.create_composition(
                        db,
                        project_id=project.ProjectID,
                        material_id=mat_id,
                        filler_id=fil_id,
                        weight_percentage=wp,
                        addition_method=str(comp.get("AdditionMethod") or "") or None,
                        remarks=str(comp.get("Remarks") or "") or None,
                    )
                    compositions_created += 1

        result: dict[str, Any] = {
            "persisted": bool(created_ids),
            "target_table": "tbl_ProjectInfo",
            "created_ids": created_ids,
            "created_count": len(created_ids),
            "project_names": project_names,
            "formula_codes": formula_codes,
            "compositions_created": compositions_created,
            "skipped": skipped,
        }
        if len(created_ids) == 1:
            result["created_id"] = created_ids[0]
            result["project_name"] = project_names[0]
            result["formula_code"] = formula_codes[0]
        return result

    # ── formula_composition (standalone) ──────────────────────────────

    @staticmethod
    async def _persist_formula_compositions(
        db: AsyncSession,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        from app.api.v1.modules.projects.crud import CompositionCRUD
        from app.api.v1.modules.projects.model import ProjectModel

        rows_by_project: dict[str, list[dict[str, Any]]] = {}

        items = data.get("items")
        if isinstance(items, list) and items:
            for comp in items:
                if not isinstance(comp, dict):
                    continue
                row_project_name = str(comp.get("ProjectName") or "").strip()
                if not row_project_name:
                    row_project_name = str(data.get("ProjectName") or "").strip()
                if not row_project_name:
                    continue
                rows_by_project.setdefault(row_project_name, []).append(comp)
        else:
            project_name = str(data.get("ProjectName") or "").strip()
            if project_name:
                rows_by_project[project_name] = [data]

        if not rows_by_project:
            return {
                "persisted": False,
                "reason": "ProjectName required for formula_composition",
            }

        created_count = 0
        created_by_project: dict[str, int] = {}
        skipped: list[str] = []

        for project_name, rows in rows_by_project.items():
            proj_result = await db.execute(
                sa_select(ProjectModel).where(ProjectModel.ProjectName == project_name)
            )
            project = proj_result.scalar_one_or_none()
            if not project:
                skipped.append(f"project_not_found: {project_name}")
                continue

            for comp in rows:
                wp = AgentIngestService._safe_float(comp.get("WeightPercentage"))
                if wp is None:
                    skipped.append(f"missing_weight_percentage: {project_name}")
                    continue

                mat_id = await AgentIngestService._resolve_material_name(
                    db,
                    comp.get("MaterialName") or comp.get("MaterialTradeName"),
                )
                fil_id = await AgentIngestService._resolve_filler_name(
                    db,
                    comp.get("FillerName") or comp.get("FillerTradeName"),
                )
                await CompositionCRUD.create_composition(
                    db,
                    project_id=project.ProjectID,
                    material_id=mat_id,
                    filler_id=fil_id,
                    weight_percentage=wp,
                    addition_method=str(comp.get("AdditionMethod") or "") or None,
                    remarks=str(comp.get("Remarks") or "") or None,
                )
                created_count += 1
                created_by_project[project_name] = (
                    created_by_project.get(project_name, 0) + 1
                )

        return {
            "persisted": bool(created_count),
            "target_table": "tbl_FormulaComposition",
            "created_count": created_count,
            "created_by_project": created_by_project,
            "skipped": skipped,
        }

    # ── test results (ink / coating / 3dprint / composite) ────────────

    @staticmethod
    async def _persist_test_result(
        db: AsyncSession,
        target: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        from app.api.v1.modules.projects.model import ProjectModel
        from app.api.v1.modules.test_results.crud import TestResultCRUD

        rows = data.get("items") if isinstance(data.get("items"), list) else [data]

        dispatch = {
            "test_results_ink": (
                "tbl_TestResults_Ink",
                TestResultCRUD.create_ink_result,
            ),
            "test_results_coating": (
                "tbl_TestResults_Coating",
                TestResultCRUD.create_coating_result,
            ),
            "test_results_3dprint": (
                "tbl_TestResults_3DPrint",
                TestResultCRUD.create_3dprint_result,
            ),
            "test_results_composite": (
                "tbl_TestResults_Composite",
                TestResultCRUD.create_composite_result,
            ),
        }

        entry = dispatch.get(target)
        if not entry:
            return {"persisted": False, "reason": f"Unknown test result type: {target}"}

        tbl_name, create_fn = entry

        created_result_ids: list[int] = []
        skipped: list[str] = []

        for row in rows:
            if not isinstance(row, dict):
                skipped.append("invalid row")
                continue

            project_name = str(row.get("ProjectName") or "").strip()
            if not project_name:
                skipped.append("missing ProjectName")
                continue

            proj_result = await db.execute(
                sa_select(ProjectModel).where(ProjectModel.ProjectName == project_name)
            )
            project = proj_result.scalar_one_or_none()
            if not project:
                skipped.append(f"project_not_found: {project_name}")
                continue

            excluded_keys = {"ProjectName", "target_table"}
            kwargs = {
                k: v for k, v in row.items() if k not in excluded_keys and v is not None
            }
            if "TestDate" in kwargs:
                kwargs["TestDate"] = AgentIngestService._safe_date(kwargs["TestDate"])

            try:
                created = await create_fn(db, project_id=project.ProjectID, **kwargs)
                created_result_ids.append(created.ResultID)
            except Exception as exc:  # noqa: BLE001
                skipped.append(f"create_failed: {project_name}: {type(exc).__name__}")

        return {
            "persisted": bool(created_result_ids),
            "target_table": tbl_name,
            "result_ids": created_result_ids,
            "created_count": len(created_result_ids),
            "skipped": skipped,
        }

    # ── Reference-data lookup helpers ─────────────────────────────────

    @staticmethod
    async def _find_or_create_material_category(
        db: AsyncSession,
        name: str,
    ) -> int:
        """Return CategoryID for *name*, creating the row if needed."""
        from app.api.v1.modules.materials.model import MaterialCategoryModel

        row = await db.execute(
            sa_select(MaterialCategoryModel).where(
                MaterialCategoryModel.CategoryName == name
            )
        )
        cat = row.scalar_one_or_none()
        if cat:
            return cat.CategoryID

        new_cat = MaterialCategoryModel(CategoryName=name)
        db.add(new_cat)
        await db.flush()
        await db.refresh(new_cat)
        return new_cat.CategoryID

    @staticmethod
    async def _find_or_create_filler_type(
        db: AsyncSession,
        name: str,
    ) -> int:
        """Return FillerTypeID for *name*, creating the row if needed."""
        from app.api.v1.modules.fillers.model import FillerTypeModel

        row = await db.execute(
            sa_select(FillerTypeModel).where(FillerTypeModel.FillerTypeName == name)
        )
        ft = row.scalar_one_or_none()
        if ft:
            return ft.FillerTypeID

        new_ft = FillerTypeModel(FillerTypeName=name)
        db.add(new_ft)
        await db.flush()
        await db.refresh(new_ft)
        return new_ft.FillerTypeID

    @staticmethod
    async def _find_or_create_project_type(
        db: AsyncSession,
        name: str,
    ) -> int:
        """Return TypeID for *name*, creating the row if needed."""
        from app.api.v1.modules.projects.model import ProjectTypeModel

        row = await db.execute(
            sa_select(ProjectTypeModel).where(ProjectTypeModel.TypeName == name)
        )
        pt = row.scalar_one_or_none()
        if pt:
            return pt.TypeID

        code = name[:3].upper() if len(name) >= 3 else name.upper().ljust(3, "X")
        new_pt = ProjectTypeModel(TypeName=name, TypeCode=code)
        db.add(new_pt)
        await db.flush()
        await db.refresh(new_pt)
        return new_pt.TypeID

    @staticmethod
    async def _resolve_material_name(
        db: AsyncSession,
        name: Any,
    ) -> int | None:
        """Find MaterialID by TradeName.  Returns ``None`` if not found."""
        from app.api.v1.modules.materials.model import MaterialModel

        n = str(name or "").strip()
        if not n:
            return None
        row = await db.execute(
            sa_select(MaterialModel.MaterialID).where(MaterialModel.TradeName == n)
        )
        return row.scalar_one_or_none()

    @staticmethod
    async def _resolve_filler_name(
        db: AsyncSession,
        name: Any,
    ) -> int | None:
        """Find FillerID by TradeName.  Returns ``None`` if not found."""
        from app.api.v1.modules.fillers.model import FillerModel

        n = str(name or "").strip()
        if not n:
            return None
        row = await db.execute(
            sa_select(FillerModel.FillerID).where(FillerModel.TradeName == n)
        )
        return row.scalar_one_or_none()

    # ── Safe type-conversion helpers ──────────────────────────────────

    @staticmethod
    def _safe_float(val: Any) -> float | None:
        if val is None:
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _safe_int(val: Any) -> int | None:
        if val is None:
            return None
        try:
            return int(val)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _safe_date(val: Any):
        """Parse a date string into a ``date`` object (best-effort)."""
        if val is None:
            return None
        if isinstance(val, datetime):
            return val.date()
        s = str(val).strip()
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%d.%m.%Y"):
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                continue
        return None

    @staticmethod
    async def _call_mineru_api(
        file_path: str,
        source_file_name: str,
    ) -> dict[str, Any]:
        """Call MinerU API with cloud-v4 flow and local-parse fallback."""
        cfg = get_mineru_config()
        if not cfg.api_url:
            raise ExternalServiceException("MinerU", "MINERU_API_URL is empty")

        base_url = cfg.api_url.rstrip("/")
        parse_path = (cfg.parse_path or "/parse").strip()
        if not parse_path.startswith("/"):
            parse_path = f"/{parse_path}"

        auth_headers: dict[str, str] = {"Content-Type": "application/json"}
        if cfg.api_key:
            auth_headers["Authorization"] = f"Bearer {cfg.api_key}"

        # ---- Step 1: Request presigned upload URL ----
        batch_payload = {
            "files": [{"name": source_file_name, "is_ocr": True}],
            "model_version": "vlm",
            "enable_formula": True,
            "enable_table": True,
            "language": "ch",
        }

        def _request_upload_url() -> requests.Response:
            return requests.post(
                f"{base_url}/file-urls/batch",
                headers=auth_headers,
                json=batch_payload,
                timeout=30,
            )

        resp_batch = await asyncio.to_thread(_request_upload_url)
        if resp_batch.status_code == 404:
            logger.warning(
                "MinerU batch endpoint not found (404), fallback to local parse endpoint: %s%s",
                base_url,
                parse_path,
            )
            return await AgentIngestService._call_mineru_parse_api(
                file_path=file_path,
                source_file_name=source_file_name,
                cfg=cfg,
                base_url=base_url,
            )

        if resp_batch.status_code >= 400:
            raise ExternalServiceException(
                "MinerU",
                f"Batch submit HTTP {resp_batch.status_code}: {resp_batch.text[:300]}",
            )

        body_batch = resp_batch.json()
        if body_batch.get("code") != 0:
            raise ExternalServiceException(
                "MinerU",
                f"Batch submit error: {body_batch.get('msg', 'unknown')}",
            )

        batch_id = body_batch["data"]["batch_id"]
        file_urls = body_batch["data"].get("file_urls") or []
        if not file_urls:
            raise ExternalServiceException("MinerU", "No presigned upload URL returned")

        logger.info(
            "MinerU batch created, batch_id=%s, uploading %s",
            batch_id,
            source_file_name,
        )

        # ---- Step 2: Upload file to presigned URL ----
        upload_url = file_urls[0]

        def _upload_file() -> requests.Response:
            with open(file_path, "rb") as fobj:
                return requests.put(upload_url, data=fobj, timeout=60)

        resp_upload = await asyncio.to_thread(_upload_file)
        if resp_upload.status_code >= 300:
            raise ExternalServiceException(
                "MinerU",
                f"File upload HTTP {resp_upload.status_code}",
            )

        logger.info("MinerU file uploaded successfully, waiting for task creation...")

        # ---- Step 3: Wait for MinerU to scan and auto-submit parsing task ----
        # After file upload, MinerU's system scans the uploaded file and creates
        # the parsing task automatically. This takes a few seconds.
        await asyncio.sleep(8)

        # ---- Step 4: Poll for task completion ----
        # Batch result endpoint: /extract-results/batch/{batch_id}
        # Note: NOT /extract/task/batch/{batch_id} (that endpoint returns 404)
        poll_url = f"{base_url}/extract-results/batch/{batch_id}"
        poll_url_fallback = f"{base_url}/extract/task/{batch_id}"
        switched_poll_endpoint = False
        max_seconds = cfg.timeout_seconds or 300
        poll_interval = 5
        elapsed = 0

        while elapsed < max_seconds:
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

            def _poll_result() -> requests.Response:
                return requests.get(poll_url, headers=auth_headers, timeout=30)

            try:
                resp_poll = await asyncio.to_thread(_poll_result)
            except Exception as poll_exc:
                logger.warning(
                    "MinerU poll request failed: %s, retrying... (elapsed=%ss)",
                    poll_exc,
                    elapsed,
                )
                continue

            if resp_poll.status_code == 404:
                if not switched_poll_endpoint and poll_url != poll_url_fallback:
                    switched_poll_endpoint = True
                    poll_url = poll_url_fallback
                    logger.warning(
                        "MinerU poll endpoint returned 404, switching to task poll endpoint: %s",
                        poll_url,
                    )
                    continue
                raise ExternalServiceException(
                    "MinerU",
                    "Poll endpoint returned 404. "
                    f"Current poll_url={poll_url}. "
                    "Please verify MINERU_API_URL matches cloud-v4 API host, "
                    "and validate MinerU poll endpoint compatibility for your account.",
                )

            if resp_poll.status_code >= 500:
                logger.warning(
                    "MinerU poll HTTP %s, body=%s, retrying... (elapsed=%ss)",
                    resp_poll.status_code,
                    resp_poll.text[:200],
                    elapsed,
                )
                continue

            if resp_poll.status_code >= 400:
                raise ExternalServiceException(
                    "MinerU",
                    f"Poll HTTP {resp_poll.status_code}: {resp_poll.text[:300]}",
                )

            body_poll = resp_poll.json()
            poll_code = body_poll.get("code")

            if poll_code != 0:
                logger.warning(
                    "MinerU poll code=%s, msg=%s, retrying... (elapsed=%ss)",
                    poll_code,
                    body_poll.get("msg", ""),
                    elapsed,
                )
                continue

            task_data = body_poll.get("data", {})

            # --- Try to find individual task results ---
            # MinerU batch result uses "extract_result" (array of task results)
            extract_results = (
                task_data.get("extract_result")
                or task_data.get("extract_results")
                or []
            )

            if isinstance(extract_results, list) and extract_results:
                first_task = extract_results[0]
                state = first_task.get("state", "")
            elif task_data.get("state"):
                # Batch-level state (some API versions put state at data level)
                first_task = task_data
                state = task_data["state"]
            else:
                # No results yet — task may still be initializing
                logger.info(
                    "MinerU poll: no extract_result yet, batch_id=%s, "
                    "data_keys=%s, elapsed=%ss/%ss",
                    batch_id,
                    list(task_data.keys()),
                    elapsed,
                    max_seconds,
                )
                continue

            if state == "done":
                zip_url = first_task.get("full_zip_url", "")
                logger.info(
                    "MinerU task done, batch_id=%s, zip_url=%s",
                    batch_id,
                    zip_url[:80] if zip_url else "(empty)",
                )
                if zip_url:
                    return await AgentIngestService._download_mineru_result(
                        zip_url, source_file_name
                    )
                return {
                    "raw_text": "",
                    "structured_content": first_task,
                    "source": "mineru_cloud",
                }
            elif state == "failed":
                err_msg = first_task.get("err_msg", "unknown error")
                raise ExternalServiceException("MinerU", f"Parse failed: {err_msg}")
            else:
                # pending / running / converting
                progress = first_task.get("extract_progress", {})
                logger.info(
                    "MinerU task state=%s, progress=%s, elapsed=%ss/%ss",
                    state,
                    progress or "N/A",
                    elapsed,
                    max_seconds,
                )

        raise ExternalServiceException(
            "MinerU", f"Polling timed out after {max_seconds}s"
        )

    @staticmethod
    async def _call_mineru_parse_api(
        *,
        file_path: str,
        source_file_name: str,
        cfg: Any,
        base_url: str,
    ) -> dict[str, Any]:
        parse_path = (getattr(cfg, "parse_path", "") or "/parse").strip()
        if not parse_path.startswith("/"):
            parse_path = f"/{parse_path}"
        parse_url = f"{base_url}{parse_path}"

        headers: dict[str, str] = {}
        if getattr(cfg, "api_key", ""):
            headers["Authorization"] = f"Bearer {cfg.api_key}"

        guessed_type = (
            mimetypes.guess_type(source_file_name)[0] or "application/octet-stream"
        )

        def _invoke_parse() -> requests.Response:
            with open(file_path, "rb") as fobj:
                return requests.post(
                    parse_url,
                    headers=headers,
                    files={"file": (source_file_name, fobj, guessed_type)},
                    timeout=getattr(cfg, "timeout_seconds", 30) or 30,
                )

        response = await asyncio.to_thread(_invoke_parse)
        if response.status_code >= 400:
            raise ExternalServiceException(
                "MinerU",
                f"Parse API HTTP {response.status_code}: {response.text[:300]}",
            )

        try:
            payload = response.json()
        except json.JSONDecodeError:
            payload = {
                "raw_text": response.text,
                "source": "mineru_parse_api",
            }

        normalized = AgentIngestService._normalize_mineru_response(payload)
        normalized["source"] = "mineru_parse_api"
        return normalized

    @staticmethod
    async def _download_mineru_result(
        zip_url: str,
        source_file_name: str,
    ) -> dict[str, Any]:
        """Download MinerU result zip and extract markdown/JSON content.

        Uses multiple download strategies to handle SSL issues on Windows:
        1. Normal requests.get
        2. Custom SSL context with relaxed settings
        3. PowerShell Invoke-WebRequest (Windows native TLS stack)
        """
        import io
        import zipfile as _zipfile

        zip_bytes = await asyncio.to_thread(
            AgentIngestService._download_with_ssl_fallback, zip_url
        )

        raw_text = ""
        structured_content: dict[str, Any] = {}

        with _zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            for name in sorted(zf.namelist()):
                if name.endswith(".md") and not raw_text:
                    raw_text = zf.read(name).decode("utf-8", errors="replace")
                elif name.endswith(".json"):
                    try:
                        content = json.loads(
                            zf.read(name).decode("utf-8", errors="replace")
                        )
                        if isinstance(content, dict):
                            structured_content.update(content)
                        elif isinstance(content, list):
                            structured_content["content_list"] = content
                    except json.JSONDecodeError:
                        pass

        logger.info(
            "MinerU result downloaded: markdown=%d chars, json_keys=%s",
            len(raw_text),
            list(structured_content.keys())[:10],
        )

        return {
            "raw_text": raw_text,
            "structured_content": structured_content,
            "source": "mineru_cloud",
            "file_name": source_file_name,
        }

    @staticmethod
    def _download_with_ssl_fallback(url: str) -> bytes:
        """Download a URL with proxy-bypass and SSL fallback strategies.

        Root cause: proxy software (Clash/V2Ray etc.) intercepts DNS for
        cdn-mineru.openxlab.org.cn, returning a fake IP (198.18.x.x), but
        fails to relay the TLS connection properly.

        Strategy 1: requests with explicit proxy bypass (NO_PROXY)
        Strategy 2: Direct socket connection via real DNS (bypass proxy)
        Strategy 3: curl.exe with --noproxy flag
        """
        import socket
        import ssl
        import subprocess
        import tempfile
        import time
        import urllib.request

        # --- Strategy 1: requests with proxy bypass ---
        # Tell requests to NOT use any proxy for this CDN domain
        no_proxy = {"http": None, "https": None}
        for attempt in range(2):
            try:
                resp = requests.get(url, timeout=90, proxies=no_proxy)
                resp.raise_for_status()
                logger.info(
                    "MinerU ZIP downloaded via requests+no_proxy (%d bytes, attempt %d)",
                    len(resp.content),
                    attempt + 1,
                )
                return resp.content
            except Exception as exc:
                logger.warning(
                    "Strategy 1 (requests+no_proxy) attempt %d failed: %s",
                    attempt + 1,
                    exc,
                )
                time.sleep(2)

        # --- Strategy 2: Resolve real IP via public DNS, then connect directly ---
        try:
            data = AgentIngestService._download_via_real_dns(url)
            logger.info(
                "MinerU ZIP downloaded via real DNS bypass (%d bytes)", len(data)
            )
            return data
        except Exception as exc:
            logger.warning("Strategy 2 (real DNS bypass) failed: %s", exc)

        # --- Strategy 3: curl.exe with --noproxy ---
        try:
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                tmp_path = tmp.name

            result = subprocess.run(
                [
                    "curl.exe",
                    "-sS",
                    "-L",
                    "--noproxy",
                    "*",
                    "--connect-timeout",
                    "15",
                    "--max-time",
                    "120",
                    "-o",
                    tmp_path,
                    url,
                ],
                capture_output=True,
                text=True,
                timeout=130,
            )
            if result.returncode == 0:
                import os

                data = Path(tmp_path).read_bytes()
                os.unlink(tmp_path)
                if len(data) > 100:  # sanity check
                    logger.info(
                        "MinerU ZIP downloaded via curl.exe --noproxy (%d bytes)",
                        len(data),
                    )
                    return data
                logger.warning("curl.exe returned too-small file (%d bytes)", len(data))
            else:
                logger.warning(
                    "Strategy 3 (curl --noproxy) failed: exit=%d, stderr=%s",
                    result.returncode,
                    result.stderr[:300],
                )
        except FileNotFoundError:
            logger.warning("Strategy 3: curl.exe not found")
        except Exception as exc:
            logger.warning("Strategy 3 (curl --noproxy) failed: %s", exc)

        raise ExternalServiceException(
            "MinerU",
            "ZIP download failed — CDN (cdn-mineru.openxlab.org.cn) is "
            "unreachable, likely blocked by local proxy software. "
            "Please add *.openxlab.org.cn to your proxy's DIRECT/bypass rules.",
        )

    @staticmethod
    def _download_via_real_dns(url: str) -> bytes:
        """Bypass local proxy DNS by resolving via public DNS (114.114.114.114),
        then connect directly to the real IP with proper SNI."""
        import socket
        import ssl
        import struct
        from urllib.parse import urlparse

        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        port = parsed.port or 443
        path = parsed.path
        if parsed.query:
            path += f"?{parsed.query}"

        # --- Resolve hostname via public DNS (114.114.114.114) ---
        real_ip = AgentIngestService._resolve_via_public_dns(hostname)
        if not real_ip:
            raise ExternalServiceException(
                "MinerU", f"Failed to resolve {hostname} via public DNS"
            )

        logger.info(
            "Real DNS resolution: %s → %s (bypassing proxy DNS)", hostname, real_ip
        )

        # --- Connect directly to real IP with SNI ---
        ctx = ssl.create_default_context()
        # CDN certificates should be valid, but allow fallback
        try:
            raw_sock = socket.create_connection((real_ip, port), timeout=30)
            ssl_sock = ctx.wrap_socket(raw_sock, server_hostname=hostname)
        except ssl.SSLError:
            # Retry without verification
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            raw_sock = socket.create_connection((real_ip, port), timeout=30)
            ssl_sock = ctx.wrap_socket(raw_sock, server_hostname=hostname)

        try:
            # Send HTTP GET request
            request_line = (
                f"GET {path} HTTP/1.1\r\n"
                f"Host: {hostname}\r\n"
                f"User-Agent: MinerU-Agent/1.0\r\n"
                f"Accept: */*\r\n"
                f"Connection: close\r\n"
                f"\r\n"
            )
            ssl_sock.sendall(request_line.encode("utf-8"))

            # Read response
            response_data = b""
            while True:
                chunk = ssl_sock.recv(65536)
                if not chunk:
                    break
                response_data += chunk
        finally:
            ssl_sock.close()

        # Parse HTTP response
        header_end = response_data.find(b"\r\n\r\n")
        if header_end == -1:
            raise ExternalServiceException("MinerU", "Invalid HTTP response from CDN")

        header_section = response_data[:header_end].decode("utf-8", errors="replace")
        body = response_data[header_end + 4 :]

        # Check status
        status_line = header_section.split("\r\n")[0]
        if (
            "200" not in status_line
            and "301" not in status_line
            and "302" not in status_line
        ):
            raise ExternalServiceException("MinerU", f"CDN returned: {status_line}")

        # Handle redirects
        if "301" in status_line or "302" in status_line:
            for line in header_section.split("\r\n"):
                if line.lower().startswith("location:"):
                    redirect_url = line.split(":", 1)[1].strip()
                    logger.info("CDN redirect → %s", redirect_url[:80])
                    # For redirect, try normal requests (redirect target might not be proxied)
                    resp = requests.get(
                        redirect_url, timeout=90, proxies={"http": None, "https": None}
                    )
                    resp.raise_for_status()
                    return resp.content
            raise ExternalServiceException(
                "MinerU", "CDN redirect without Location header"
            )

        # Handle chunked transfer encoding
        if b"transfer-encoding: chunked" in header_section.lower().encode():
            body = AgentIngestService._decode_chunked(body)

        return body

    @staticmethod
    def _resolve_via_public_dns(
        hostname: str, dns_server: str = "114.114.114.114"
    ) -> str | None:
        """Resolve hostname using a specific DNS server (bypasses local proxy DNS)."""
        import socket
        import struct

        try:
            # Build DNS query packet
            query_id = 0x1234
            flags = 0x0100  # standard query, recursion desired
            questions = 1

            packet = struct.pack(">HHHHHH", query_id, flags, questions, 0, 0, 0)

            # Encode domain name
            for part in hostname.split("."):
                packet += struct.pack("B", len(part)) + part.encode("ascii")
            packet += b"\x00"  # end of domain name
            packet += struct.pack(">HH", 1, 1)  # Type A, Class IN

            # Send to DNS server
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            sock.sendto(packet, (dns_server, 53))
            data, _ = sock.recvfrom(1024)
            sock.close()

            # Parse response — skip header (12 bytes) and question section
            offset = 12
            # Skip question section
            while data[offset] != 0:
                offset += data[offset] + 1
            offset += 5  # null byte + type(2) + class(2)

            # Parse answer section
            answer_count = struct.unpack(">H", data[6:8])[0]
            for _ in range(answer_count):
                # Skip name (could be pointer or label)
                if data[offset] & 0xC0 == 0xC0:
                    offset += 2  # pointer
                else:
                    while data[offset] != 0:
                        offset += data[offset] + 1
                    offset += 1

                rtype, rclass, ttl, rdlength = struct.unpack(
                    ">HHIH", data[offset : offset + 10]
                )
                offset += 10

                if rtype == 1 and rdlength == 4:  # A record
                    ip = socket.inet_ntoa(data[offset : offset + 4])
                    # Skip fake proxy IPs (198.18.0.0/15)
                    if not ip.startswith("198.18."):
                        return ip

                offset += rdlength

            return None
        except Exception as exc:
            logger.warning("Public DNS resolution failed: %s", exc)
            return None

    @staticmethod
    def _decode_chunked(data: bytes) -> bytes:
        """Decode HTTP chunked transfer encoding."""
        result = b""
        pos = 0
        while pos < len(data):
            # Find chunk size line
            line_end = data.find(b"\r\n", pos)
            if line_end == -1:
                break
            size_str = data[pos:line_end].decode("ascii", errors="replace").strip()
            if not size_str:
                pos = line_end + 2
                continue
            try:
                chunk_size = int(size_str, 16)
            except ValueError:
                break
            if chunk_size == 0:
                break
            chunk_start = line_end + 2
            result += data[chunk_start : chunk_start + chunk_size]
            pos = chunk_start + chunk_size + 2  # skip \r\n after chunk
        return result

    @staticmethod
    async def _call_deepseek_structuring(mineru_output: dict[str, Any]) -> str:
        cfg = get_deepseek_config()
        client = create_deepseek_client()

        # Pre-process: extract meaningful content, filter MinerU internal metadata
        cleaned = AgentIngestService._clean_mineru_output_for_llm(mineru_output)

        system_prompt = (
            "You are a chemical industry document analyzer. Extract structured "
            "information from OCR/parsed document output and map it to database "
            "tables in a formulation management system.\n"
            "The system manages: raw materials, inorganic fillers, "
            "projects/formulations, formula compositions, "
            "and test results (ink, coating, 3D printing, composite).\n"
            "Return valid JSON only, no markdown fences."
        )
        user_prompt = (
            "Analyze this document and extract structured data.\n\n"
            "STEP 1 - Identify which database table this data belongs to (choose ONE):\n"
            "  raw_materials: material/resin/monomer/oligomer/additive data sheets\n"
            "  fillers: inorganic filler/particle specifications\n"
            "  project: formulation/project descriptions\n"
            "  formula_composition: ingredient lists with weight percentages\n"
            "  test_results_ink: inkjet printing test data\n"
            "  test_results_coating: coating/film test data\n"
            "  test_results_3dprint: 3D printing/additive manufacturing test data\n"
            "  test_results_composite: composite material test data\n"
            "  unknown: cannot determine\n\n"
            "STEP 2 - Extract domain-specific fields for the identified table:\n"
            "  raw_materials: TradeName*, Supplier, CAS_Number, Density(number), "
            "Viscosity(number), FunctionDescription, CategoryName\n"
            "  fillers: TradeName*, Supplier, ParticleSize, IsSilanized(0/1), "
            "CouplingAgent, SurfaceArea(number), FillerTypeName\n"
            "  project: ProjectName*, ProjectTypeName(one of: Inkjet/Coating/"
            "3D Printing/Composite), SubstrateApplication, FormulatorName, "
            "FormulationDate(YYYY-MM-DD), compositions(array of "
            "{MaterialName,FillerName,WeightPercentage,AdditionMethod,Remarks})\n"
            "  formula_composition: ProjectName*, items(array of "
            "{MaterialName,FillerName,WeightPercentage*,AdditionMethod,Remarks})\n"
            "  test_results_ink: ProjectName, Ink_Viscosity, Ink_Reactivity, "
            "Ink_ParticleSize, Ink_SurfaceTension, Ink_ColorValue, TestDate, Notes\n"
            "  test_results_coating: ProjectName, Coating_Adhesion, "
            "Coating_Transparency, Coating_SurfaceHardness, "
            "Coating_ChemicalResistance, Coating_CostEstimate, TestDate, Notes\n"
            "  test_results_3dprint: ProjectName, Print3D_Shrinkage, "
            "Print3D_YoungsModulus, Print3D_FlexuralStrength, "
            "Print3D_ShoreHardness, Print3D_ImpactResistance, TestDate, Notes\n"
            "  test_results_composite: ProjectName, Composite_FlexuralStrength, "
            "Composite_YoungsModulus, Composite_ImpactResistance, "
            "Composite_ConversionRate, Composite_WaterAbsorption, TestDate, Notes\n"
            "(* = required field, number = numeric value)\n\n"
            "Return JSON with this exact structure:\n"
            "{\n"
            '  "document_summary": "brief content summary",\n'
            '  "entities": ["named entities found"],\n'
            '  "properties": {"key": "value pairs"},\n'
            '  "raw_text_excerpt": "first 500 chars of actual text",\n'
            '  "target_table": "one_of_the_table_names_above",\n'
            '  "domain_data": { fields for the target table }\n'
            "}\n\n"
            "RULES:\n"
            "- Extract ACTUAL CONTENT from the document, not metadata.\n"
            "- Numeric values must be numbers, not strings.\n"
            "- If multiple items of same type, put them in domain_data.items array.\n"
            "- For formula_composition, domain_data.items is an array of ingredients.\n"
            "- For project with compositions, include them in domain_data.compositions.\n\n"
            f"INPUT:\n{json.dumps(cleaned, ensure_ascii=False)}"
        )

        def _invoke() -> str:
            response = client.chat.completions.create(
                model=cfg.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
            )
            return response.choices[0].message.content or "{}"

        return await asyncio.to_thread(_invoke)

    @staticmethod
    def _normalize_csv_header(header: Any) -> str:
        normalized = str(header or "").strip().lower().replace("\ufeff", "")
        return re.sub(r"[\s_\-./:;()\[\]{}]+", "", normalized)

    @staticmethod
    def _pick_csv_value(row: dict[str, Any], aliases: tuple[str, ...]) -> str:
        for alias in aliases:
            value = row.get(alias)
            if value is None:
                continue
            text = str(value).strip()
            if text:
                return text
        return ""

    @staticmethod
    def _normalize_project_type_name(raw_value: str) -> str:
        value = str(raw_value or "").strip()
        if not value:
            return ""

        normalized = AgentIngestService._normalize_csv_header(value)
        mapping = {
            "inkjet": "Inkjet",
            "coating": "Coating",
            "3dprinting": "3D Printing",
            "3dprint": "3D Printing",
            "composite": "Composite",
        }
        return mapping.get(normalized, value)

    @staticmethod
    def _build_structured_data_from_csv(
        mineru_output: dict[str, Any],
    ) -> dict[str, Any] | None:
        structured = mineru_output.get("structured_content")
        if not isinstance(structured, dict):
            return None

        rows = structured.get("rows")
        if not isinstance(rows, list) or not rows:
            return None

        project_name_aliases = ("projectname", "prname")
        project_type_aliases = ("projecttypename", "type")
        formulator_aliases = ("formulatorname", "formulator")
        date_aliases = ("formulationdate", "date", "testdate")
        substrate_aliases = (
            "substrateapplication",
            "sa",
            "application",
        )

        material_aliases = ("materialname", "materialtradename", "material")
        filler_aliases = ("fillername", "fillertradename", "filler")
        weight_aliases = ("weightpercentage", "weightpercent", "wt", "wtpercent")
        addition_aliases = ("additionmethod",)
        remarks_aliases = ("remarks", "remark", "notes", "note")

        trade_name_aliases = ("tradename",)
        supplier_aliases = ("supplier",)
        cas_aliases = ("casnumber", "cas")
        density_aliases = ("density",)
        viscosity_aliases = ("viscosity",)
        function_aliases = ("functiondescription", "function")
        material_category_aliases = ("categoryname", "category")

        particle_size_aliases = ("particlesize", "d50")
        silanized_aliases = ("issilanized", "silanized")
        coupling_aliases = ("couplingagent",)
        surface_area_aliases = ("surfacearea",)
        filler_type_aliases = ("fillertypename", "fillertype")

        ink_field_aliases = (
            "inkviscosity",
            "inkreactivity",
            "inkparticlesize",
            "inksurfacetension",
            "inkcolorvalue",
            "inkrheologynote",
        )
        coating_field_aliases = (
            "coatingadhesion",
            "coatingtransparency",
            "coatingsurfacehardness",
            "coatingchemicalresistance",
            "coatingcostestimate",
        )
        print3d_field_aliases = (
            "print3dshrinkage",
            "print3dyoungsmodulus",
            "print3dflexuralstrength",
            "print3dshorehardness",
            "print3dimpactresistance",
        )
        composite_field_aliases = (
            "compositeflexuralstrength",
            "compositeyoungsmodulus",
            "compositeimpactresistance",
            "compositeconversionrate",
            "compositewaterabsorption",
        )

        normalized_headers: set[str] = set()
        for row in rows:
            if isinstance(row, dict):
                normalized_headers = {
                    AgentIngestService._normalize_csv_header(key) for key in row.keys()
                }
                break

        if not normalized_headers:
            return None

        normalized_rows: list[dict[str, Any]] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            normalized_rows.append(
                {
                    AgentIngestService._normalize_csv_header(key): value
                    for key, value in row.items()
                }
            )

        def _has_any(aliases: tuple[str, ...]) -> bool:
            return any(alias in normalized_headers for alias in aliases)

        target_table = "unknown"
        if _has_any(project_name_aliases) and _has_any(weight_aliases):
            target_table = "formula_composition"
        elif _has_any(trade_name_aliases) and _has_any(
            cas_aliases
            + density_aliases
            + viscosity_aliases
            + material_category_aliases
        ):
            target_table = "raw_materials"
        elif _has_any(trade_name_aliases) and _has_any(
            particle_size_aliases
            + silanized_aliases
            + coupling_aliases
            + surface_area_aliases
            + filler_type_aliases
        ):
            target_table = "fillers"
        elif _has_any(project_name_aliases) and _has_any(ink_field_aliases):
            target_table = "test_results_ink"
        elif _has_any(project_name_aliases) and _has_any(coating_field_aliases):
            target_table = "test_results_coating"
        elif _has_any(project_name_aliases) and _has_any(print3d_field_aliases):
            target_table = "test_results_3dprint"
        elif _has_any(project_name_aliases) and _has_any(composite_field_aliases):
            target_table = "test_results_composite"
        elif _has_any(project_name_aliases):
            target_table = "project"
        else:
            return None

        items: list[dict[str, Any]] = []
        for normalized_row in normalized_rows:
            if target_table == "project":
                project_name = AgentIngestService._pick_csv_value(
                    normalized_row, project_name_aliases
                )
                if not project_name:
                    continue
                item: dict[str, Any] = {"ProjectName": project_name}
                project_type = AgentIngestService._pick_csv_value(
                    normalized_row, project_type_aliases
                )
                normalized_type = AgentIngestService._normalize_project_type_name(
                    project_type
                )
                if normalized_type:
                    item["ProjectTypeName"] = normalized_type
                formulator = AgentIngestService._pick_csv_value(
                    normalized_row, formulator_aliases
                )
                if formulator:
                    item["FormulatorName"] = formulator
                formulation_date = AgentIngestService._pick_csv_value(
                    normalized_row, date_aliases
                )
                if formulation_date:
                    item["FormulationDate"] = formulation_date
                substrate_application = AgentIngestService._pick_csv_value(
                    normalized_row, substrate_aliases
                )
                if substrate_application:
                    item["SubstrateApplication"] = substrate_application
                items.append(item)
                continue

            if target_table == "formula_composition":
                project_name = AgentIngestService._pick_csv_value(
                    normalized_row, project_name_aliases
                )
                weight_percentage = AgentIngestService._pick_csv_value(
                    normalized_row, weight_aliases
                )
                if not project_name or not weight_percentage:
                    continue
                item = {
                    "ProjectName": project_name,
                    "WeightPercentage": weight_percentage,
                }
                material_name = AgentIngestService._pick_csv_value(
                    normalized_row, material_aliases
                )
                if material_name:
                    item["MaterialName"] = material_name
                filler_name = AgentIngestService._pick_csv_value(
                    normalized_row, filler_aliases
                )
                if filler_name:
                    item["FillerName"] = filler_name
                addition_method = AgentIngestService._pick_csv_value(
                    normalized_row, addition_aliases
                )
                if addition_method:
                    item["AdditionMethod"] = addition_method
                remarks = AgentIngestService._pick_csv_value(
                    normalized_row, remarks_aliases
                )
                if remarks:
                    item["Remarks"] = remarks
                items.append(item)
                continue

            if target_table == "raw_materials":
                trade_name = AgentIngestService._pick_csv_value(
                    normalized_row, trade_name_aliases
                )
                if not trade_name:
                    continue
                item = {"TradeName": trade_name}
                supplier = AgentIngestService._pick_csv_value(
                    normalized_row, supplier_aliases
                )
                if supplier:
                    item["Supplier"] = supplier
                cas_number = AgentIngestService._pick_csv_value(
                    normalized_row, cas_aliases
                )
                if cas_number:
                    item["CAS_Number"] = cas_number
                density = AgentIngestService._pick_csv_value(
                    normalized_row, density_aliases
                )
                if density:
                    item["Density"] = density
                viscosity = AgentIngestService._pick_csv_value(
                    normalized_row, viscosity_aliases
                )
                if viscosity:
                    item["Viscosity"] = viscosity
                function_desc = AgentIngestService._pick_csv_value(
                    normalized_row, function_aliases
                )
                if function_desc:
                    item["FunctionDescription"] = function_desc
                category_name = AgentIngestService._pick_csv_value(
                    normalized_row, material_category_aliases
                )
                if category_name:
                    item["CategoryName"] = category_name
                items.append(item)
                continue

            if target_table == "fillers":
                trade_name = AgentIngestService._pick_csv_value(
                    normalized_row, trade_name_aliases
                )
                if not trade_name:
                    continue
                item = {"TradeName": trade_name}
                supplier = AgentIngestService._pick_csv_value(
                    normalized_row, supplier_aliases
                )
                if supplier:
                    item["Supplier"] = supplier
                particle_size = AgentIngestService._pick_csv_value(
                    normalized_row, particle_size_aliases
                )
                if particle_size:
                    item["ParticleSize"] = particle_size
                is_silanized = AgentIngestService._pick_csv_value(
                    normalized_row, silanized_aliases
                )
                if is_silanized:
                    lowered = is_silanized.strip().lower()
                    if lowered in {"1", "true", "yes", "y"}:
                        item["IsSilanized"] = 1
                    elif lowered in {"0", "false", "no", "n"}:
                        item["IsSilanized"] = 0
                    else:
                        item["IsSilanized"] = is_silanized
                coupling_agent = AgentIngestService._pick_csv_value(
                    normalized_row, coupling_aliases
                )
                if coupling_agent:
                    item["CouplingAgent"] = coupling_agent
                surface_area = AgentIngestService._pick_csv_value(
                    normalized_row, surface_area_aliases
                )
                if surface_area:
                    item["SurfaceArea"] = surface_area
                filler_type = AgentIngestService._pick_csv_value(
                    normalized_row, filler_type_aliases
                )
                if filler_type:
                    item["FillerTypeName"] = filler_type
                items.append(item)
                continue

            project_name = AgentIngestService._pick_csv_value(
                normalized_row, project_name_aliases
            )
            if not project_name:
                continue
            item = {"ProjectName": project_name}
            if target_table == "test_results_ink":
                for field in (
                    "Ink_Viscosity",
                    "Ink_Reactivity",
                    "Ink_ParticleSize",
                    "Ink_SurfaceTension",
                    "Ink_ColorValue",
                    "Ink_RheologyNote",
                ):
                    value = AgentIngestService._pick_csv_value(
                        normalized_row,
                        (AgentIngestService._normalize_csv_header(field),),
                    )
                    if value:
                        item[field] = value
            elif target_table == "test_results_coating":
                for field in (
                    "Coating_Adhesion",
                    "Coating_Transparency",
                    "Coating_SurfaceHardness",
                    "Coating_ChemicalResistance",
                    "Coating_CostEstimate",
                ):
                    value = AgentIngestService._pick_csv_value(
                        normalized_row,
                        (AgentIngestService._normalize_csv_header(field),),
                    )
                    if value:
                        item[field] = value
            elif target_table == "test_results_3dprint":
                for field in (
                    "Print3D_Shrinkage",
                    "Print3D_YoungsModulus",
                    "Print3D_FlexuralStrength",
                    "Print3D_ShoreHardness",
                    "Print3D_ImpactResistance",
                ):
                    value = AgentIngestService._pick_csv_value(
                        normalized_row,
                        (AgentIngestService._normalize_csv_header(field),),
                    )
                    if value:
                        item[field] = value
            elif target_table == "test_results_composite":
                for field in (
                    "Composite_FlexuralStrength",
                    "Composite_YoungsModulus",
                    "Composite_ImpactResistance",
                    "Composite_ConversionRate",
                    "Composite_WaterAbsorption",
                ):
                    value = AgentIngestService._pick_csv_value(
                        normalized_row,
                        (AgentIngestService._normalize_csv_header(field),),
                    )
                    if value:
                        item[field] = value

            test_date = AgentIngestService._pick_csv_value(normalized_row, date_aliases)
            if test_date:
                item["TestDate"] = test_date
            notes = AgentIngestService._pick_csv_value(normalized_row, remarks_aliases)
            if notes:
                item["Notes"] = notes
            items.append(item)

        if not items:
            return None

        raw_excerpt = str(mineru_output.get("raw_text") or "")[:1000]
        headers_meta = structured.get("headers")
        if not isinstance(headers_meta, list):
            headers_meta = sorted(normalized_headers)

        return {
            "document_summary": f"CSV parsed into {len(items)} {target_table} rows",
            "entities": [],
            "properties": {
                "source": "csv_local",
                "row_count": len(items),
                "headers": headers_meta,
            },
            "raw_text_excerpt": raw_excerpt,
            "target_table": target_table,
            "domain_data": {
                "items": items,
            },
        }

    @staticmethod
    async def _parse_csv_locally(file_path: str) -> dict[str, Any]:
        def _read_csv() -> dict[str, Any]:
            encodings = ["utf-8-sig", "utf-8", "gbk"]
            last_error: Exception | None = None
            for encoding in encodings:
                try:
                    with open(
                        file_path, "r", encoding=encoding, newline=""
                    ) as csv_file:
                        reader = csv.DictReader(csv_file)
                        rows = [row for row in reader]
                    return {
                        "raw_text": "\n".join(
                            [", ".join(row.values()) for row in rows[:50]]
                        ),
                        "structured_content": {
                            "headers": list(rows[0].keys()) if rows else [],
                            "rows": rows,
                            "row_count": len(rows),
                        },
                        "source": "csv_local",
                    }
                except Exception as exc:  # noqa: BLE001
                    last_error = exc
            raise ValidationException(f"Failed to parse CSV: {last_error}")

        return await asyncio.to_thread(_read_csv)

    @staticmethod
    def _normalize_mineru_response(payload: Any) -> dict[str, Any]:
        if not isinstance(payload, dict):
            return {
                "raw_text": str(payload),
                "structured_content": {},
                "source": "mineru",
            }

        payload_dict: dict[str, Any] = payload
        raw_candidate = payload_dict.get("data")
        candidate: dict[str, Any]
        if isinstance(raw_candidate, dict):
            candidate = raw_candidate
        else:
            candidate = payload_dict

        raw_text = ""
        for key in ("raw_text", "text", "content", "markdown"):
            value = candidate.get(key)
            if isinstance(value, str) and value.strip():
                raw_text = value.strip()
                break

        structured_content = candidate.get("structured")
        if structured_content is None:
            structured_content = candidate.get("result")
        if structured_content is None:
            structured_content = {
                k: v
                for k, v in candidate.items()
                if k not in {"raw_text", "text", "content", "markdown"}
            }

        return {
            "raw_text": raw_text,
            "structured_content": structured_content,
            "source": "mineru",
        }

    @staticmethod
    def _clean_mineru_output_for_llm(mineru_output: dict[str, Any]) -> dict[str, Any]:
        """Pre-process MinerU output before sending to Deepseek for structuring.

        Removes MinerU internal metadata fields (like _backend, _ocr_enable,
        pdf_info, _version_name) that confuse the LLM into thinking the content
        is empty or just metadata. Extracts actual document content from
        content_list and raw_text.
        """
        raw_text = str(mineru_output.get("raw_text") or "").strip()
        source = mineru_output.get("source", "unknown")
        file_name = mineru_output.get("file_name", "")
        warning = mineru_output.get("warning", "")

        structured = mineru_output.get("structured_content") or {}

        # Extract actual content from MinerU's content_list
        content_items: list[Any] = []
        if isinstance(structured, dict):
            # content_list contains the actual parsed text blocks
            raw_content_list = structured.get("content_list") or []
            if isinstance(raw_content_list, list):
                for item in raw_content_list:
                    if isinstance(item, dict):
                        # Each item has "type" and "text" (or other fields)
                        content_items.append(item)
                    elif isinstance(item, str) and item.strip():
                        content_items.append({"text": item})

        # Build a clean, content-focused output for the LLM
        cleaned: dict[str, Any] = {
            "file_name": file_name,
            "source": source,
        }

        if raw_text:
            cleaned["raw_text"] = raw_text[:3000]  # cap to avoid token overflow

        if content_items:
            cleaned["content_blocks"] = content_items[:50]  # cap to avoid overflow

        if warning:
            cleaned["processing_note"] = warning

        # If source is fallback and no content, note that explicitly
        if source == "fallback" and not raw_text and not content_items:
            cleaned["processing_note"] = (
                "OCR processing was unavailable. Only file metadata is available."
            )

        return cleaned

    @staticmethod
    def _fallback_structured_data(mineru_output: dict[str, Any]) -> dict[str, Any]:
        structured = mineru_output.get("structured_content")
        raw_text = str(mineru_output.get("raw_text") or "")
        excerpt = raw_text[:1000]

        return {
            "document_summary": "Fallback extraction used",
            "entities": [],
            "records": structured if isinstance(structured, list) else [],
            "properties": structured if isinstance(structured, dict) else {},
            "raw_text_excerpt": excerpt,
            "source": "fallback",
        }

    @staticmethod
    def _safe_parse_json(content: str) -> dict[str, Any] | None:
        content = (content or "").strip()
        if not content:
            return None

        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                return parsed
            return {"output": parsed}
        except json.JSONDecodeError:
            pass

        match = re.search(r"\{[\s\S]*\}", content)
        if not match:
            return None

        try:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, dict):
                return parsed
            return {"output": parsed}
        except json.JSONDecodeError:
            return None

    @staticmethod
    def _build_fallback_parse_result(
        file_path: str,
        source_file_name: str,
        warning: str,
    ) -> dict[str, Any]:
        return {
            "raw_text": "",
            "structured_content": {
                "file_name": source_file_name,
                "file_path": file_path,
            },
            "source": "fallback",
            "warning": warning,
        }

    @staticmethod
    def _sanitize_filename(file_name: str) -> str:
        safe = re.sub(r"[^A-Za-z0-9._-]", "_", file_name)
        safe = safe.strip("._")
        return safe or "uploaded_file"

    @staticmethod
    def _build_storage_path(task_id: int, safe_filename: str) -> Path:
        now = datetime.now()
        suffix = Path(safe_filename).suffix or ".bin"
        stem = Path(safe_filename).stem or "source"

        target_dir = (
            settings.AGENT_UPLOAD_DIR
            / str(now.year)
            / f"{now.month:02d}"
            / f"{now.day:02d}"
            / f"task_{task_id}"
        )
        target_filename = f"{stem}_{task_id}{suffix}"
        return target_dir / target_filename

    @staticmethod
    def _normalize_task_status(raw_status: str) -> str:
        if raw_status == "success":
            return AgentTaskStatus.succeeded.value
        return raw_status


class AgentChatService:
    """Chat orchestration for Agent Phase 4."""

    @staticmethod
    async def handle_chat(
        db: AsyncSession,
        background_tasks: BackgroundTasks,
        request: AgentChatRequest,
        current_user: dict[str, Any],
        file: UploadFile | None = None,
    ) -> AgentChatResponse:
        started_at = datetime.now()
        user_id = int(current_user.get("user_id") or 0)
        user_role = str(current_user.get("role") or "user")
        user_name = str(current_user.get("username") or "")
        intent = AgentChatIntent.general
        AgentIngestService._ensure_agent_role(user_role)

        try:
            execute_plan_task_id = AgentDbAdminService.parse_plan_execute_command(
                request.message
            )
            if execute_plan_task_id is not None:
                AgentIngestService._ensure_mutation_role(user_role)
                execute_result = await AgentDbAdminService.execute_plan_task(
                    db,
                    task_id=execute_plan_task_id,
                    user_id=user_id,
                    user_role=user_role,
                )
                response = AgentChatResponse(
                    mode=AgentChatMode.sync,
                    intent=AgentChatIntent.mutate_domain,
                    reply=f"Database change plan #{execute_plan_task_id} has been executed.",
                    query_result={
                        "plan_task_id": execute_plan_task_id,
                        "execution": execute_result,
                    },
                    tool_traces=[
                        AgentToolTrace(
                            tool_name="agent_db_change_executor",
                            status="ok",
                            tool_input={
                                "task_id": execute_plan_task_id,
                            },
                            tool_output=execute_result,
                        )
                    ],
                )
                response.audit_id = await AgentChatService._append_chat_audit_log(
                    db=db,
                    user_id=user_id,
                    action_type="chat_change_plan_executed",
                    user_input={
                        "message": request.message,
                        "username": user_name,
                        "role": user_role,
                    },
                    tool_trace={
                        "tool_traces": [
                            item.model_dump(mode="json")
                            for item in response.tool_traces
                        ],
                    },
                    response_payload=response,
                    started_at=started_at,
                    task_id=execute_plan_task_id,
                )
                return response

            intent = await AgentChatService._infer_intent(
                request.message, has_file=file is not None
            )

            if file is not None:
                submit_result = await AgentIngestService.submit_ingest_task(
                    db=db,
                    background_tasks=background_tasks,
                    file=file,
                    user_id=user_id,
                    user_role=user_role,
                )

                ingest_preview_raw = agent_document_ingest.invoke(
                    {
                        "file_path": submit_result.file_path,
                        "file_type": Path(file.filename or "").suffix.lower(),
                    }
                )
                ingest_preview = AgentChatService._safe_parse_json(
                    ingest_preview_raw
                ) or {"raw": str(ingest_preview_raw)}

                response = AgentChatResponse(
                    mode=AgentChatMode.async_task,
                    intent=AgentChatIntent.ingest,
                    reply=(
                        f"Ingestion task created (task_id={submit_result.task_id}). "
                        "Poll /api/v1/agent/tasks/{id} for status."
                    ),
                    task_id=submit_result.task_id,
                    tool_traces=[
                        AgentToolTrace(
                            tool_name="agent_document_ingest",
                            status="ok",
                            tool_input={
                                "file_name": file.filename,
                                "file_path": submit_result.file_path,
                            },
                            tool_output=ingest_preview,
                        )
                    ],
                )
                response.audit_id = await AgentChatService._append_chat_audit_log(
                    db=db,
                    user_id=user_id,
                    action_type="chat_ingest_submitted",
                    user_input={
                        "message": request.message,
                        "username": user_name,
                        "role": user_role,
                    },
                    tool_trace={
                        "tool_traces": [
                            item.model_dump(mode="json")
                            for item in response.tool_traces
                        ],
                    },
                    response_payload=response,
                    started_at=started_at,
                    task_id=submit_result.task_id,
                )
                return response

            if intent in {
                AgentChatIntent.mutate_domain,
                AgentChatIntent.mutate_bulk,
                AgentChatIntent.admin_ops,
            }:
                plan = await AgentDbAdminService.build_change_plan(request.message)
                if not plan:
                    follow_up = (
                        "I could not reliably parse this database change request. "
                        "Please provide clearer details: domain/action/target_id/payload."
                    )
                    response = AgentChatResponse(
                        mode=AgentChatMode.follow_up,
                        intent=AgentChatIntent.clarify,
                        reply=follow_up,
                        follow_up_question=follow_up,
                        degraded=True,
                        retryable=False,
                    )
                    response.audit_id = await AgentChatService._append_chat_audit_log(
                        db=db,
                        user_id=user_id,
                        action_type="chat_change_plan_clarify",
                        user_input={
                            "message": request.message,
                            "username": user_name,
                            "role": user_role,
                        },
                        tool_trace={"reason": "plan_parse_failed"},
                        response_payload=response,
                        started_at=started_at,
                    )
                    return response

                plan_intent = str(plan.get("intent") or "clarify")
                if plan_intent == "admin_ops":
                    AgentIngestService._ensure_admin_role(user_role)
                elif plan_intent in {"mutate_domain", "mutate_bulk"}:
                    AgentIngestService._ensure_mutation_role(user_role)

                if plan_intent == "clarify":
                    reason = str(
                        plan.get("reason")
                        or "Insufficient information to generate an executable plan."
                    )
                    response = AgentChatResponse(
                        mode=AgentChatMode.follow_up,
                        intent=AgentChatIntent.clarify,
                        reply=reason,
                        follow_up_question=reason,
                    )
                    response.audit_id = await AgentChatService._append_chat_audit_log(
                        db=db,
                        user_id=user_id,
                        action_type="chat_change_plan_clarify",
                        user_input={
                            "message": request.message,
                            "username": user_name,
                            "role": user_role,
                        },
                        tool_trace={"plan": plan},
                        response_payload=response,
                        started_at=started_at,
                    )
                    return response

                (
                    preview_result,
                    rollback_snapshot,
                ) = await AgentDbAdminService.build_preview_and_snapshot(db, plan)
                plan_task_id = await AgentDbAdminService.submit_change_plan_task(
                    db,
                    message=request.message,
                    user_id=user_id,
                    user_role=user_role,
                    plan=plan,
                    preview_result=preview_result,
                    rollback_snapshot=rollback_snapshot,
                )
                plan_summary = str(
                    plan.get("summary") or "A database change plan has been generated"
                )
                response_intent = AgentChatService._intent_from_plan(plan_intent)
                response = AgentChatResponse(
                    mode=AgentChatMode.follow_up,
                    intent=response_intent,
                    reply=(
                        f"{plan_summary}. Plan task ID={plan_task_id}. "
                        f"If confirmed, send: execute plan {plan_task_id}"
                    ),
                    follow_up_question=(
                        f"If you want to execute it, send: execute plan {plan_task_id}"
                    ),
                    task_id=plan_task_id,
                    query_result={
                        "plan_task_id": plan_task_id,
                        "plan": plan,
                        "preview_result": preview_result,
                        "rollback_snapshot": rollback_snapshot,
                        "execution_instruction": f"execute plan {plan_task_id}",
                    },
                    tool_traces=[
                        AgentToolTrace(
                            tool_name="agent_db_change_planner",
                            status="ok",
                            tool_input={
                                "message": request.message,
                            },
                            tool_output={
                                "plan": plan,
                                "preview_result": preview_result,
                                "rollback_snapshot": rollback_snapshot,
                            },
                        )
                    ],
                )
                response.audit_id = await AgentChatService._append_chat_audit_log(
                    db=db,
                    user_id=user_id,
                    action_type="chat_change_plan_created",
                    user_input={
                        "message": request.message,
                        "username": user_name,
                        "role": user_role,
                    },
                    tool_trace={
                        "tool_traces": [
                            item.model_dump(mode="json")
                            for item in response.tool_traces
                        ],
                    },
                    response_payload=response,
                    started_at=started_at,
                    task_id=plan_task_id,
                )
                return response

            if AgentChatService._requires_scope(
                user_role, intent, request.project_scope
            ):
                follow_up = (
                    "Your account requires project scope for this query. "
                    "Please provide project_scope (for example [1,2,3]) "
                    "and I will run the structured query."
                )
                response = AgentChatResponse(
                    mode=AgentChatMode.follow_up,
                    intent=AgentChatIntent.clarify,
                    reply=follow_up,
                    follow_up_question=follow_up,
                )
                response.audit_id = await AgentChatService._append_chat_audit_log(
                    db=db,
                    user_id=user_id,
                    action_type="chat_follow_up",
                    user_input={
                        "message": request.message,
                        "username": user_name,
                        "role": user_role,
                    },
                    tool_trace={"reason": "missing_project_scope"},
                    response_payload=response,
                    started_at=started_at,
                )
                return response

            response = await AgentChatService._run_react_chat(
                request=request,
                intent=intent,
                user_role=user_role,
                user_id=user_id,
            )
            response.audit_id = await AgentChatService._append_chat_audit_log(
                db=db,
                user_id=user_id,
                action_type="chat_completed"
                if not response.degraded
                else "chat_degraded",
                user_input={
                    "message": request.message,
                    "username": user_name,
                    "role": user_role,
                    "project_scope": request.project_scope,
                },
                tool_trace={
                    "tool_traces": [
                        item.model_dump(mode="json") for item in response.tool_traces
                    ],
                },
                response_payload=response,
                started_at=started_at,
            )
            return response
        except ExternalServiceException as exc:
            degraded = AgentChatResponse(
                mode=AgentChatMode.follow_up,
                intent=intent,
                reply="External AI service is currently unavailable. Please try again later.",
                degraded=True,
                retryable=True,
            )
            degraded.audit_id = await AgentChatService._append_chat_audit_log(
                db=db,
                user_id=user_id,
                action_type="chat_degraded",
                user_input={
                    "message": request.message,
                    "username": user_name,
                    "role": user_role,
                },
                tool_trace={"error": f"{type(exc).__name__}: {exc}"},
                response_payload=degraded,
                started_at=started_at,
            )
            return degraded
        except ValidationException as exc:
            degraded = AgentChatResponse(
                mode=AgentChatMode.follow_up,
                intent=intent,
                reply=str(exc),
                degraded=True,
                retryable=False,
            )
            degraded.audit_id = await AgentChatService._append_chat_audit_log(
                db=db,
                user_id=user_id,
                action_type="chat_failed",
                user_input={
                    "message": request.message,
                    "username": user_name,
                    "role": user_role,
                },
                tool_trace={"error": f"{type(exc).__name__}: {exc}"},
                response_payload=degraded,
                started_at=started_at,
            )
            return degraded
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Agent chat failed, user_id=%s, role=%s, error=%s: %s",
                user_id,
                user_role,
                type(exc).__name__,
                exc,
                exc_info=True,
            )
            raise DatabaseException("Agent chat execution failed") from exc

    @staticmethod
    async def _run_react_chat(
        request: AgentChatRequest,
        intent: AgentChatIntent,
        user_role: str = "user",
        user_id: int = 0,
    ) -> AgentChatResponse:
        callback_handler = AgentAuditCallbackHandler()
        tool_traces: list[AgentToolTrace] = []
        context_token = set_agent_request_context(
            AgentRequestContext(
                user_id=user_id,
                user_role=user_role,
                project_scope=request.project_scope,
                top_k=request.top_k,
            )
        )

        prompt = AgentChatService._build_react_prompt(
            message=request.message,
            project_scope=request.project_scope,
            top_k=request.top_k,
            user_role=user_role,
        )

        try:
            executor = build_react_agent()
            result = await executor.ainvoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ]
                },
                config={
                    "callbacks": [callback_handler],
                    "recursion_limit": settings.AGENT_REACT_RECURSION_LIMIT,
                },
            )
            tool_traces = AgentChatService._build_tool_traces(callback_handler.events)
            query_result = AgentChatService._extract_query_result(tool_traces)
            reply = AgentChatService._extract_reply_from_agent_result(result)

            if AgentChatService._is_insufficient_steps_reply(reply):
                logger.warning(
                    "ReAct returned insufficient-steps reply, switching to deterministic fallback"
                )
                if intent == AgentChatIntent.query:
                    return await AgentChatService._run_direct_sql_fallback(request)
                return await AgentChatService._run_direct_llm_fallback(request, intent)

            if query_result and query_result.get("ok") is False:
                safe_reply = (
                    "Query execution failed, so I cannot provide record-level results. "
                    "Please retry or verify table/schema availability."
                )
                return AgentChatResponse(
                    mode=AgentChatMode.follow_up,
                    intent=intent,
                    reply=safe_reply,
                    follow_up_question=(
                        "Please retry the query or provide a narrower request."
                    ),
                    query_result=query_result,
                    tool_traces=tool_traces,
                    degraded=True,
                    retryable=True,
                )

            if query_result and query_result.get("ok") is True:
                formatted_text = str(query_result.get("formatted_text") or "").strip()
                if formatted_text:
                    reply = formatted_text

            if not reply and query_result and query_result.get("ok") is True:
                reply = query_result.get("formatted_text") or "Query completed."

            if not reply:
                reply = "Request processed."

            return AgentChatResponse(
                mode=AgentChatMode.sync,
                intent=intent,
                reply=reply,
                query_result=query_result,
                tool_traces=tool_traces,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "ReAct chat failed, fallback to direct handling: %s: %s",
                type(exc).__name__,
                exc,
            )
        finally:
            reset_agent_request_context(context_token)

        if intent == AgentChatIntent.query:
            return await AgentChatService._run_direct_sql_fallback(request)

        return await AgentChatService._run_direct_llm_fallback(request, intent)

    @staticmethod
    async def _run_direct_sql_fallback(request: AgentChatRequest) -> AgentChatResponse:
        service = TextToSqlService()
        result = await service.run_query(
            QueryRequestSchema(
                question=request.message,
                top_k=request.top_k,
                project_scope=request.project_scope,
            )
        )

        query_result = {
            "sql": result.sql,
            "columns": result.columns,
            "rows": result.rows,
            "row_count": result.row_count,
            "retries": result.retries,
            "duration_ms": result.duration_ms,
            "formatted_text": result.formatted_text,
            "warning": result.warning,
        }
        return AgentChatResponse(
            mode=AgentChatMode.sync,
            intent=AgentChatIntent.query,
            reply=result.formatted_text or "Query completed.",
            query_result=query_result,
            tool_traces=[
                AgentToolTrace(
                    tool_name="agent_text_to_sql_direct_fallback",
                    status="ok",
                    tool_input={
                        "question": request.message,
                        "top_k": request.top_k,
                        "project_scope": request.project_scope,
                    },
                    tool_output=query_result,
                )
            ],
            degraded=True,
            retryable=False,
        )

    @staticmethod
    async def _run_direct_llm_fallback(
        request: AgentChatRequest,
        intent: AgentChatIntent,
    ) -> AgentChatResponse:
        cfg = get_deepseek_config()
        if not cfg.api_key:
            return AgentChatResponse(
                mode=AgentChatMode.follow_up,
                intent=intent,
                reply="DEEPSEEK_API_KEY is not configured. General chat is unavailable.",
                degraded=True,
                retryable=False,
            )

        client = create_deepseek_client()

        def _invoke() -> str:
            completion = client.chat.completions.create(
                model=cfg.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a concise assistant for internal API users.",
                    },
                    {
                        "role": "user",
                        "content": request.message,
                    },
                ],
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
            )
            return completion.choices[0].message.content or ""

        try:
            reply = await asyncio.to_thread(_invoke)
            return AgentChatResponse(
                mode=AgentChatMode.sync,
                intent=intent,
                reply=reply.strip() or "Request processed.",
                degraded=True,
                retryable=False,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Direct LLM fallback failed: %s: %s",
                type(exc).__name__,
                exc,
            )
            return AgentChatResponse(
                mode=AgentChatMode.follow_up,
                intent=intent,
                reply="Chat service is temporarily unavailable. Please try again later.",
                degraded=True,
                retryable=True,
            )

    # ------------------------------------------------------------------
    # Intent classification
    # ------------------------------------------------------------------

    _INTENT_CLASSIFICATION_PROMPT = (
        "You are an intent classifier for an internal database & document management system.\n"
        "Classify the user message into exactly ONE of the following categories:\n"
        "- query   : user wants to look up, search, count, list, compare, or retrieve data "
        "(projects, materials, fillers, formulas, test results, etc.)\n"
        "- ingest  : user wants to upload, import, parse, extract, or OCR a file/document\n"
        "- mutate_domain : user wants to create/update/delete a single domain record\n"
        "- mutate_bulk   : user wants batch/multi-record updates or deletes\n"
        "- admin_ops     : schema/DDL/permission/index/admin database operations\n"
        "- general       : greeting, chitchat, or anything else not related to data operations\n\n"
        "Respond with ONLY one single word from: query, ingest, mutate_domain, mutate_bulk, admin_ops, general.\n\n"
        "User message:\n{message}"
    )

    @staticmethod
    async def _infer_intent(message: str, has_file: bool) -> AgentChatIntent:
        """Classify user intent using LLM first, keyword fallback if LLM unavailable."""
        if has_file:
            return AgentChatIntent.ingest

        # 1) Try LLM-based classification (fast, temperature=0, max_tokens=10)
        try:
            result = await AgentChatService._llm_classify_intent(message)
            if result is not None:
                return result
        except Exception:  # noqa: BLE001
            logger.debug(
                "LLM intent classification unavailable, using keyword fallback"
            )

        # 2) Keyword fallback (bilingual)
        return AgentChatService._keyword_classify_intent(message)

    @staticmethod
    async def _llm_classify_intent(message: str) -> AgentChatIntent | None:
        cfg = get_deepseek_config()
        if not cfg.api_key:
            return None

        client = create_deepseek_client()
        prompt = AgentChatService._INTENT_CLASSIFICATION_PROMPT.format(message=message)

        def _invoke() -> str:
            response = client.chat.completions.create(
                model=cfg.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=10,
            )
            return (response.choices[0].message.content or "").strip().lower()

        raw = await asyncio.to_thread(_invoke)

        if "query" in raw:
            return AgentChatIntent.query
        if "ingest" in raw:
            return AgentChatIntent.ingest
        if "mutate_bulk" in raw:
            return AgentChatIntent.mutate_bulk
        if "mutate_domain" in raw:
            return AgentChatIntent.mutate_domain
        if "admin_ops" in raw:
            return AgentChatIntent.admin_ops
        if "general" in raw:
            return AgentChatIntent.general
        return None

    @staticmethod
    def _keyword_classify_intent(message: str) -> AgentChatIntent:
        """Keyword fallback when LLM is unavailable."""
        lowered = (message or "").lower()

        admin_keywords = [
            "ddl",
            "schema",
            "alter table",
            "create table",
            "drop table",
            "index",
            "grant",
            "revoke",
        ]
        if any(kw in lowered for kw in admin_keywords):
            return AgentChatIntent.admin_ops

        mutation_keywords = [
            "create",
            "add",
            "insert",
            "update",
            "edit",
            "delete",
            "remove",
        ]
        bulk_keywords = [
            "batch",
            "bulk",
            "all",
            "multiple",
        ]
        has_mutation = any(kw in lowered for kw in mutation_keywords)
        has_bulk = any(kw in lowered for kw in bulk_keywords)
        if has_mutation and has_bulk:
            return AgentChatIntent.mutate_bulk
        if has_mutation:
            return AgentChatIntent.mutate_domain

        query_keywords = [
            "formulator",
            "query",
            "search",
            "find",
            "list",
            "show",
            "display",
            "count",
            "how many",
            "what",
            "which",
            "who",
            "get",
            "fetch",
            "look up",
            "project",
            "material",
            "filler",
            "formula",
            "test",
            "result",
            "select",
            "where",
            "sql",
            "table",
            "column",
            "record",
        ]
        if any(kw in lowered for kw in query_keywords):
            return AgentChatIntent.query

        ingest_keywords = [
            "ingest",
            "upload",
            "import",
            "parse",
            "extract",
            "ocr",
        ]
        if any(kw in lowered for kw in ingest_keywords):
            return AgentChatIntent.ingest

        return AgentChatIntent.general

    @staticmethod
    def _requires_scope(
        user_role: str,
        intent: AgentChatIntent,
        project_scope: list[int] | None,
    ) -> bool:
        if intent != AgentChatIntent.query:
            return False
        auth_cfg = get_agent_authorization_config()
        return auth_cfg.requires_project_scope(user_role) and not project_scope

    @staticmethod
    def _intent_from_plan(plan_intent: str) -> AgentChatIntent:
        normalized = str(plan_intent or "").strip().lower()
        if normalized == "mutate_bulk":
            return AgentChatIntent.mutate_bulk
        if normalized == "admin_ops":
            return AgentChatIntent.admin_ops
        if normalized == "mutate_domain":
            return AgentChatIntent.mutate_domain
        if normalized == "query":
            return AgentChatIntent.query
        if normalized == "ingest":
            return AgentChatIntent.ingest
        return AgentChatIntent.clarify

    @staticmethod
    def _is_insufficient_steps_reply(reply: str) -> bool:
        normalized = str(reply or "").strip().lower()
        if not normalized:
            return False
        signatures = [
            "need more steps to process this request",
            "sorry, need more steps",
            "unable to complete within remaining steps",
            "insufficient steps",
        ]
        return any(signature in normalized for signature in signatures)

    @staticmethod
    def _build_react_prompt(
        *,
        message: str,
        project_scope: list[int] | None,
        top_k: int,
        user_role: str = "user",
    ) -> str:
        scope_text = json.dumps(project_scope or [], ensure_ascii=False)

        # --- scope instruction varies by role ---
        if project_scope:
            scope_instruction = (
                f"A project_scope filter is provided: {scope_text}. "
                "Pass it to agent_text_to_sql when calling."
            )
        elif user_role in ("admin", "superadmin"):
            scope_instruction = (
                "No project_scope filter is set. You are an admin — "
                "execute queries across ALL projects without restriction."
            )
        else:
            scope_instruction = (
                "No project_scope filter is set. "
                "For general statistics or full-table queries, proceed without a filter. "
                "Only ask the user for project_scope when the question is clearly about "
                "specific projects and cannot be answered without it."
            )

        return (
            "You are an English-first bilingual (English/Chinese) database assistant for a "
            "photopolymer formulation management system.\n\n"
            "Available tables:\n"
            "  tbl_ProjectInfo          — projects (ProjectName, FormulaCode, FormulatorName …)\n"
            "  tbl_RawMaterials         — raw materials\n"
            "  tbl_InorganicFillers     — inorganic fillers\n"
            "  tbl_FormulaComposition   — formula compositions linked to projects\n"
            "  tbl_TestResults_Ink      — ink test results\n"
            "  tbl_TestResults_Coating  — coating test results\n"
            "  tbl_TestResults_3DPrint  — 3D printing test results\n"
            "  tbl_TestResults_Composite — composite test results\n\n"
            f"Context: top_k={top_k}, project_scope={scope_text}, user_role={user_role}\n\n"
            "Rules:\n"
            "1) ACTION FIRST: When the user asks about data, call agent_text_to_sql "
            "IMMEDIATELY. Do NOT ask the user to rephrase, confirm, or provide extra info "
            "when you can construct a reasonable query.\n"
            "2) Use agent_document_ingest ONLY when the user explicitly provides a local "
            "file path for document ingestion.\n"
            f"3) {scope_instruction}\n"
            "4) Reply in English by default. If the user clearly writes in Chinese, reply in Chinese.\n"
            "5) Be concise and action-oriented: execute first, explain after.\n\n"
            f"User question:\n{message}"
        )

    @staticmethod
    def _extract_reply_from_agent_result(result: Any) -> str:
        if not isinstance(result, dict):
            return str(result or "").strip()

        messages = result.get("messages")
        if isinstance(messages, list) and messages:
            last_message = messages[-1]
            content = getattr(last_message, "content", "")
            if isinstance(content, str):
                return content.strip()
            if isinstance(content, list):
                fragments = []
                for item in content:
                    if isinstance(item, dict):
                        fragments.append(str(item.get("text") or ""))
                    else:
                        fragments.append(str(item))
                return "".join(fragments).strip()

        return str(result.get("output") or "").strip()

    @staticmethod
    def _build_tool_traces(events: list[dict[str, Any]]) -> list[AgentToolTrace]:
        merged: dict[str, dict[str, Any]] = {}
        order: list[str] = []

        for event in events:
            run_id = str(event.get("run_id") or "")
            if not run_id:
                continue
            if run_id not in merged:
                merged[run_id] = {
                    "tool_name": "unknown_tool",
                    "status": "skipped",
                    "tool_input": None,
                    "tool_output": None,
                    "error": None,
                    "duration_ms": None,
                }
                order.append(run_id)

            item = merged[run_id]
            if event.get("tool_name"):
                item["tool_name"] = str(event["tool_name"])

            if event.get("tool_input"):
                parsed_input = AgentChatService._safe_parse_json(event["tool_input"])
                item["tool_input"] = parsed_input or {"raw": str(event["tool_input"])}

            if event.get("status") in {"ok", "failed", "skipped"}:
                item["status"] = str(event["status"])

            if event.get("tool_output"):
                parsed_output = AgentChatService._safe_parse_json(event["tool_output"])
                item["tool_output"] = parsed_output or {
                    "raw": str(event["tool_output"])
                }

            if event.get("error"):
                item["error"] = str(event["error"])

            if event.get("duration_ms") is not None:
                try:
                    item["duration_ms"] = int(event["duration_ms"])
                except Exception:  # noqa: BLE001
                    item["duration_ms"] = None

        traces: list[AgentToolTrace] = []
        for run_id in order:
            row = merged[run_id]
            traces.append(
                AgentToolTrace(
                    tool_name=str(row["tool_name"]),
                    status=row["status"],
                    tool_input=row["tool_input"],
                    tool_output=row["tool_output"],
                    error=row["error"],
                    duration_ms=row["duration_ms"],
                )
            )

        return traces

    @staticmethod
    def _extract_query_result(
        tool_traces: list[AgentToolTrace],
    ) -> dict[str, Any] | None:
        for trace in reversed(tool_traces):
            if "text_to_sql" not in trace.tool_name:
                continue
            output = trace.tool_output or {}
            if output.get("ok") is False:
                return {
                    "ok": False,
                    "error": output.get("error"),
                }
            if output.get("ok") is True:
                return {
                    "ok": True,
                    "sql": output.get("sql"),
                    "columns": output.get("columns"),
                    "rows": output.get("rows"),
                    "row_count": output.get("row_count"),
                    "retries": output.get("retries"),
                    "duration_ms": output.get("duration_ms"),
                    "formatted_text": output.get("formatted_text"),
                    "warning": output.get("warning"),
                }
        return None

    @staticmethod
    def _safe_parse_json(raw: Any) -> dict[str, Any] | None:
        if isinstance(raw, dict):
            return raw
        if not isinstance(raw, str):
            return None
        text = raw.strip()
        if not text:
            return None
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
            return {"value": parsed}
        except json.JSONDecodeError:
            return None

    @staticmethod
    async def _append_chat_audit_log(
        *,
        db: AsyncSession,
        user_id: int,
        action_type: str,
        user_input: dict[str, Any],
        tool_trace: dict[str, Any],
        response_payload: AgentChatResponse,
        started_at: datetime,
        task_id: int | None = None,
    ) -> int | None:
        try:
            duration_ms = int((datetime.now() - started_at).total_seconds() * 1000)
            audit = await AgentCRUD.append_audit_log(
                db,
                user_id=user_id,
                task_id=task_id,
                action_type=action_type,
                user_input=user_input,
                tool_trace=tool_trace,
                final_response=json.dumps(
                    response_payload.model_dump(mode="json"), ensure_ascii=False
                ),
                duration_ms=duration_ms,
            )
            await db.commit()
            return int(getattr(audit, "AuditID", 0) or 0) or None
        except Exception:  # noqa: BLE001
            await db.rollback()
            logger.error("Failed to write agent chat audit log", exc_info=True)
            return None
