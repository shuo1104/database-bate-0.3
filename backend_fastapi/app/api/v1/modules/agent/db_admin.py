"""Deterministic DB admin planning and execution helpers for Agent chat."""

from __future__ import annotations

import asyncio
import json
import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import Date, DateTime, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.config import get_agent_authorization_config, get_deepseek_config
from app.agent.core import create_deepseek_client
from app.api.v1.modules.agent.crud import AgentCRUD
from app.api.v1.modules.agent.model import AgentTaskModel
from app.core.custom_exceptions import RecordNotFoundException, ValidationException
from app.config.settings import settings
from app.core.logger import logger


class AgentDbAdminService:
    _PLAN_PROMPT = (
        "You are a database operation planner for an internal admin assistant.\n"
        "Convert the user message into ONE JSON object only.\n"
        "Supported domain: materials, fillers, projects, compositions, test_results, database.\n"
        "Supported action: create, update, delete, batch_delete, upsert, ddl.\n"
        "If request is unclear, set intent to clarify and include reason.\n"
        "Output schema:\n"
        "{\n"
        '  "intent": "mutate_domain|mutate_bulk|admin_ops|clarify",\n'
        '  "domain": "materials|fillers|projects|compositions|test_results|database",\n'
        '  "action": "create|update|delete|batch_delete|upsert|ddl",\n'
        '  "target_id": 123,\n'
        '  "batch_ids": [1,2],\n'
        '  "test_result_type": "ink|coating|3dprint|composite",\n'
        '  "payload": {},\n'
        '  "summary": "short action summary",\n'
        '  "risk_level": "low|medium|high",\n'
        '  "reason": "only for clarify"\n'
        "}\n"
        "Rules:\n"
        "1) Use mutate_bulk only for batch_delete or multi-record updates.\n"
        "2) Use admin_ops for DDL, schema/table/index/permission operations.\n"
        "3) Never include markdown or explanation; JSON only.\n"
    )

    _CONFIRM_PATTERNS = [
        re.compile(
            r"(?:execute\s+plan|confirm\s+plan|run\s+plan)\s*[:#]?\s*(\d+)",
            re.IGNORECASE,
        ),
        re.compile(
            r"(?:approve\s+execute|approve\s+plan)\s*[:#]?\s*(\d+)", re.IGNORECASE
        ),
    ]

    @staticmethod
    def parse_plan_execute_command(message: str) -> int | None:
        text = (message or "").strip()
        for pattern in AgentDbAdminService._CONFIRM_PATTERNS:
            matched = pattern.search(text)
            if matched:
                try:
                    return int(matched.group(1))
                except Exception:  # noqa: BLE001
                    return None
        return None

    @staticmethod
    async def build_change_plan(message: str) -> dict[str, Any] | None:
        cfg = get_deepseek_config()
        if not cfg.api_key:
            return AgentDbAdminService._keyword_plan_fallback(message)

        client = create_deepseek_client()

        def _invoke() -> str:
            completion = client.chat.completions.create(
                model=cfg.model,
                messages=[
                    {"role": "system", "content": AgentDbAdminService._PLAN_PROMPT},
                    {"role": "user", "content": message},
                ],
                temperature=0,
                max_tokens=min(cfg.max_tokens, 800),
            )
            return completion.choices[0].message.content or ""

        raw = await asyncio.to_thread(_invoke)
        parsed = AgentDbAdminService._safe_parse_json(raw)
        if not parsed:
            return AgentDbAdminService._keyword_plan_fallback(message)
        return AgentDbAdminService._normalize_plan(parsed)

    @staticmethod
    async def submit_change_plan_task(
        db: AsyncSession,
        *,
        message: str,
        user_id: int,
        user_role: str,
        plan: dict[str, Any],
        preview_result: dict[str, Any],
        rollback_snapshot: dict[str, Any],
    ) -> int:
        task = await AgentCRUD.create_task(
            db,
            task_type="db_change_plan",
            status="pending",
            payload={
                "message": message,
                "user_id": user_id,
                "user_role": user_role,
                "plan": plan,
                "approval": {
                    "status": "pending",
                    "created_by_user_id": user_id,
                    "created_by_role": user_role,
                    "created_at": datetime.now().isoformat(),
                },
                "preview_result": preview_result,
                "rollback_snapshot": rollback_snapshot,
                "created_at": datetime.now().isoformat(),
            },
        )
        await db.commit()
        await db.refresh(task)
        return int(task.TaskID)

    @staticmethod
    async def execute_plan_task(
        db: AsyncSession,
        *,
        task_id: int,
        user_id: int,
        user_role: str,
    ) -> dict[str, Any]:
        auth_cfg = get_agent_authorization_config()
        if not auth_cfg.can_mutate(user_role):
            raise ValidationException(
                "Current role has no permission to execute DB change plans"
            )

        task = await AgentCRUD.get_task_by_id(db, task_id)
        if not task:
            raise RecordNotFoundException("AgentTask", task_id)
        if str(task.TaskType or "") != "db_change_plan":
            raise ValidationException("Only db_change_plan tasks can be executed")
        if str(task.Status or "") != "pending":
            raise ValidationException("This plan task is not in pending status")

        payload = task.Payload or {}
        plan = payload.get("plan") if isinstance(payload, dict) else None
        if not isinstance(plan, dict):
            raise ValidationException("Task payload has no valid plan")

        approval = payload.get("approval") if isinstance(payload, dict) else None
        approval_status = "pending"
        if isinstance(approval, dict):
            approval_status = str(approval.get("status") or "pending")

        if (
            settings.AGENT_MUTATION_REQUIRE_CONFIRMATION
            and approval_status != "approved"
        ):
            raise ValidationException(
                "Plan must be approved before execution. Use approval API first"
            )

        rollback_snapshot = (
            payload.get("rollback_snapshot") if isinstance(payload, dict) else None
        )
        if not isinstance(rollback_snapshot, dict):
            rollback_snapshot = await AgentDbAdminService.build_rollback_snapshot(
                db, plan
            )

        execution_result: dict[str, Any] | None = None
        rollback_performed = False

        try:
            await AgentCRUD.update_task(
                db,
                task,
                status="running",
                started_at=datetime.now(),
            )
            await db.commit()

            execution_result = await AgentDbAdminService._execute_change_plan(
                db,
                plan,
                operator_user_id=user_id,
                operator_role=user_role,
            )

            payload = dict(task.Payload or {})
            approval_payload = payload.get("approval")
            if not isinstance(approval_payload, dict):
                approval_payload = {}
            approval_payload["executed_by_user_id"] = user_id
            approval_payload["executed_by_role"] = user_role
            approval_payload["executed_at"] = datetime.now().isoformat()
            payload["approval"] = approval_payload
            payload["execution_result"] = execution_result
            payload["rollback_snapshot"] = rollback_snapshot

            await AgentCRUD.update_task(
                db,
                task,
                status="succeeded",
                payload=payload,
                result={"ok": True, "execution": execution_result},
                finished_at=datetime.now(),
            )
            await db.commit()
            return {
                "task_id": task_id,
                "status": "succeeded",
                "execution_result": execution_result,
                "rollback_performed": rollback_performed,
                "executed_by_user_id": user_id,
                "executed_by_role": user_role,
                "executed_at": approval_payload.get("executed_at"),
            }
        except Exception as exc:  # noqa: BLE001
            await db.rollback()
            if execution_result is not None:
                rollback_performed = await AgentDbAdminService._rollback_from_snapshot(
                    db,
                    plan=plan,
                    rollback_snapshot=rollback_snapshot,
                    execution_result=execution_result,
                )
            logger.error(
                "DB change plan execution failed: %s: %s", type(exc).__name__, exc
            )
            task_retry = await AgentCRUD.get_task_by_id(db, task_id)
            if task_retry:
                failed_payload = dict(task_retry.Payload or {})
                failed_payload["rollback_performed"] = rollback_performed
                await AgentCRUD.update_task(
                    db,
                    task_retry,
                    status="failed",
                    payload=failed_payload,
                    error_message=f"{type(exc).__name__}: {exc}",
                    finished_at=datetime.now(),
                )
                await db.commit()
            raise

    @staticmethod
    async def list_change_plan_tasks(
        db: AsyncSession,
        *,
        page: int,
        page_size: int,
        task_status: str | None = None,
        approval_status: str | None = None,
    ) -> dict[str, Any]:
        if not approval_status:
            tasks, total = await AgentCRUD.get_tasks_paginated(
                db,
                page=page,
                page_size=page_size,
                task_type="db_change_plan",
                status=task_status,
            )
            return {
                "items": [
                    AgentDbAdminService._build_plan_record(item) for item in tasks
                ],
                "total": total,
                "page": page,
                "page_size": page_size,
            }

        tasks = await AgentCRUD.get_tasks_by_type(
            db,
            task_type="db_change_plan",
            status=task_status,
        )
        filtered_records = [
            item
            for item in (AgentDbAdminService._build_plan_record(item) for item in tasks)
            if str(item.get("approval_status") or "") == approval_status
        ]
        total = len(filtered_records)
        start = (page - 1) * page_size
        end = start + page_size
        return {
            "items": filtered_records[start:end],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def approve_change_plan_task(
        db: AsyncSession,
        *,
        task_id: int,
        action: str,
        approver_user_id: int,
        approver_role: str,
        comment: str | None = None,
    ) -> dict[str, Any]:
        auth_cfg = get_agent_authorization_config()
        if not (
            auth_cfg.can_review(approver_role) or auth_cfg.can_mutate(approver_role)
        ):
            raise ValidationException("Current role cannot approve DB change plans")

        task = await AgentCRUD.get_task_by_id(db, task_id)
        if not task:
            raise RecordNotFoundException("AgentTask", task_id)
        if str(task.TaskType or "") != "db_change_plan":
            raise ValidationException("Only db_change_plan tasks can be approved")
        if str(task.Status or "") in {"running", "succeeded"}:
            raise ValidationException("Task is already running or completed")

        payload = dict(task.Payload or {})
        approval_raw = payload.get("approval")
        if isinstance(approval_raw, dict):
            approval_data: dict[str, Any] = dict(approval_raw)
        else:
            approval_data = {"status": "pending"}

        current_approval_status = str(approval_data.get("status") or "pending").lower()
        if current_approval_status in {"approved", "rejected"}:
            raise ValidationException(
                f"Plan has already been {current_approval_status} and cannot be re-reviewed"
            )

        normalized_action = str(action or "").strip().lower()
        if normalized_action == "approve":
            approval_data["status"] = "approved"
            approval_data["approved_by_user_id"] = approver_user_id
            approval_data["approved_by_role"] = approver_role
            approval_data["approved_at"] = datetime.now().isoformat()
            if comment:
                approval_data["comment"] = comment
            payload["approval"] = approval_data
            await AgentCRUD.update_task(
                db,
                task,
                status="pending",
                payload=payload,
                error_message=None,
            )
        elif normalized_action == "reject":
            approval_data["status"] = "rejected"
            approval_data["approved_by_user_id"] = approver_user_id
            approval_data["approved_by_role"] = approver_role
            approval_data["approved_at"] = datetime.now().isoformat()
            if comment:
                approval_data["comment"] = comment
            payload["approval"] = approval_data
            await AgentCRUD.update_task(
                db,
                task,
                status="failed",
                payload=payload,
                error_message=comment or "Plan rejected",
                finished_at=datetime.now(),
            )
        else:
            raise ValidationException("Approval action must be approve or reject")

        await db.commit()
        await db.refresh(task)
        return {
            "task_id": int(task.TaskID),
            "approval_status": str(approval_data.get("status") or "pending"),
            "approved_by_user_id": approval_data.get("approved_by_user_id"),
            "approved_by_role": approval_data.get("approved_by_role"),
            "approved_at": approval_data.get("approved_at"),
            "comment": approval_data.get("comment"),
        }

    @staticmethod
    async def build_preview_and_snapshot(
        db: AsyncSession,
        plan: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        normalized = AgentDbAdminService._normalize_plan(plan)
        preview = await AgentDbAdminService.build_preview_result(db, normalized)
        snapshot = await AgentDbAdminService.build_rollback_snapshot(db, normalized)
        return preview, snapshot

    @staticmethod
    async def build_preview_result(
        db: AsyncSession,
        plan: dict[str, Any],
    ) -> dict[str, Any]:
        normalized = AgentDbAdminService._normalize_plan(plan)
        domain = str(normalized.get("domain") or "")
        action = str(normalized.get("action") or "")
        payload = normalized.get("payload")
        if not isinstance(payload, dict):
            payload = {}
        target_id = normalized.get("target_id")
        batch_ids = normalized.get("batch_ids")
        if not isinstance(batch_ids, list):
            batch_ids = []

        estimated_rows = 0
        warnings: list[str] = []

        if action == "create":
            estimated_rows = 1
        elif action in {"update", "delete"}:
            exists = await AgentDbAdminService._check_target_exists(
                db,
                domain=domain,
                target_id=target_id,
                payload=payload,
                test_result_type=str(normalized.get("test_result_type") or ""),
            )
            estimated_rows = 1 if exists else 0
            if not exists:
                warnings.append("Target record not found; execution may fail or no-op")
        elif action == "batch_delete":
            ids = AgentDbAdminService._normalize_batch_ids(batch_ids)
            estimated_rows = await AgentDbAdminService._count_existing_batch_targets(
                db,
                domain=domain,
                ids=ids,
            )
            if estimated_rows < len(ids):
                warnings.append("Some IDs do not exist and will be ignored")
        elif action == "upsert":
            estimated_rows = 1
        elif action == "ddl":
            warnings.append("DDL operations are plan-only and will not auto-execute")

        return {
            "domain": domain,
            "action": action,
            "estimated_affected_rows": estimated_rows,
            "warnings": warnings,
            "generated_at": datetime.now().isoformat(),
        }

    @staticmethod
    async def build_rollback_snapshot(
        db: AsyncSession,
        plan: dict[str, Any],
    ) -> dict[str, Any]:
        normalized = AgentDbAdminService._normalize_plan(plan)
        domain = str(normalized.get("domain") or "")
        action = str(normalized.get("action") or "")
        payload = normalized.get("payload")
        if not isinstance(payload, dict):
            payload = {}
        target_id = normalized.get("target_id")
        batch_ids = normalized.get("batch_ids")
        if not isinstance(batch_ids, list):
            batch_ids = []

        records: list[dict[str, Any]] = []
        test_result_type = str(normalized.get("test_result_type") or "")

        if action in {"update", "delete"}:
            target_record = await AgentDbAdminService._fetch_target_record(
                db,
                domain=domain,
                target_id=target_id,
                payload=payload,
                test_result_type=test_result_type,
            )
            if target_record is not None:
                records.append(target_record)
        elif action == "batch_delete":
            ids = AgentDbAdminService._normalize_batch_ids(batch_ids)
            records.extend(
                await AgentDbAdminService._fetch_batch_records(
                    db,
                    domain=domain,
                    ids=ids,
                )
            )
        elif domain == "test_results":
            target_record = await AgentDbAdminService._fetch_target_record(
                db,
                domain=domain,
                target_id=target_id,
                payload=payload,
                test_result_type=test_result_type,
            )
            if target_record is not None:
                records.append(target_record)

        return {
            "domain": domain,
            "action": action,
            "test_result_type": test_result_type,
            "records": records,
            "captured_at": datetime.now().isoformat(),
        }

    @staticmethod
    def _build_plan_record(task: AgentTaskModel) -> dict[str, Any]:
        payload = task.Payload if isinstance(task.Payload, dict) else {}
        approval_raw = payload.get("approval")
        if isinstance(approval_raw, dict):
            approval: dict[str, Any] = dict(approval_raw)
        else:
            approval = {}
        plan = payload.get("plan") if isinstance(payload.get("plan"), dict) else None
        preview_result = (
            payload.get("preview_result")
            if isinstance(payload.get("preview_result"), dict)
            else None
        )
        rollback_snapshot = (
            payload.get("rollback_snapshot")
            if isinstance(payload.get("rollback_snapshot"), dict)
            else None
        )
        execution_result = (
            payload.get("execution_result")
            if isinstance(payload.get("execution_result"), dict)
            else task.Result
        )
        return {
            "task_id": int(task.TaskID),
            "task_status": str(task.Status),
            "approval_status": str(approval.get("status") or "pending"),
            "created_by_user_id": approval.get("created_by_user_id")
            or payload.get("user_id"),
            "created_by_role": approval.get("created_by_role")
            or payload.get("user_role"),
            "approved_by_user_id": approval.get("approved_by_user_id"),
            "approved_by_role": approval.get("approved_by_role"),
            "executed_by_user_id": approval.get("executed_by_user_id"),
            "executed_by_role": approval.get("executed_by_role"),
            "created_at": task.CreatedAt,
            "approved_at": approval.get("approved_at"),
            "executed_at": approval.get("executed_at"),
            "plan_summary": (plan or {}).get("summary") if plan else None,
            "plan": plan,
            "preview_result": preview_result,
            "rollback_snapshot": rollback_snapshot,
            "execution_result": execution_result,
            "error_message": task.ErrorMessage,
        }

    @staticmethod
    async def _check_target_exists(
        db: AsyncSession,
        *,
        domain: str,
        target_id: Any,
        payload: dict[str, Any],
        test_result_type: str,
    ) -> bool:
        record = await AgentDbAdminService._fetch_target_record(
            db,
            domain=domain,
            target_id=target_id,
            payload=payload,
            test_result_type=test_result_type,
        )
        return record is not None

    @staticmethod
    async def _count_existing_batch_targets(
        db: AsyncSession,
        *,
        domain: str,
        ids: list[int],
    ) -> int:
        if not ids:
            return 0
        model_cls = AgentDbAdminService._resolve_model_class(domain, "")
        if model_cls is None:
            return 0
        pk_name = AgentDbAdminService._primary_key_name(model_cls)
        pk_column = getattr(model_cls, pk_name)
        result = await db.execute(select(model_cls).where(pk_column.in_(ids)))
        rows = list(result.scalars().all())
        return len(rows)

    @staticmethod
    async def _fetch_target_record(
        db: AsyncSession,
        *,
        domain: str,
        target_id: Any,
        payload: dict[str, Any],
        test_result_type: str,
    ) -> dict[str, Any] | None:
        if domain == "test_results":
            model_cls = AgentDbAdminService._resolve_test_result_model_class(
                test_result_type
            )
            if model_cls is None:
                return None
            project_id = AgentDbAdminService._get_test_result_project_id(
                payload, target_id
            )
            if project_id is None:
                return None
            result = await db.execute(
                select(model_cls).where(
                    getattr(model_cls, "ProjectID_FK") == project_id
                )
            )
            obj = result.scalar_one_or_none()
            return AgentDbAdminService._model_to_json_dict(obj) if obj else None

        model_cls = AgentDbAdminService._resolve_model_class(domain, test_result_type)
        if model_cls is None:
            return None
        parsed_id = AgentDbAdminService._pick_int({"target_id": target_id}, "target_id")
        if parsed_id is None:
            return None
        obj = await db.get(model_cls, parsed_id)
        if obj is None:
            return None
        return AgentDbAdminService._model_to_json_dict(obj)

    @staticmethod
    async def _fetch_batch_records(
        db: AsyncSession,
        *,
        domain: str,
        ids: list[int],
    ) -> list[dict[str, Any]]:
        model_cls = AgentDbAdminService._resolve_model_class(domain, "")
        if model_cls is None:
            return []
        pk_name = AgentDbAdminService._primary_key_name(model_cls)
        pk_column = getattr(model_cls, pk_name)
        result = await db.execute(select(model_cls).where(pk_column.in_(ids)))
        rows = list(result.scalars().all())
        return [AgentDbAdminService._model_to_json_dict(item) for item in rows]

    @staticmethod
    def _resolve_model_class(domain: str, test_result_type: str) -> Any:
        from app.api.v1.modules.fillers.model import FillerModel
        from app.api.v1.modules.materials.model import MaterialModel
        from app.api.v1.modules.projects.model import (
            FormulaCompositionModel,
            ProjectModel,
        )

        if domain == "materials":
            return MaterialModel
        if domain == "fillers":
            return FillerModel
        if domain == "projects":
            return ProjectModel
        if domain == "compositions":
            return FormulaCompositionModel
        if domain == "test_results":
            return AgentDbAdminService._resolve_test_result_model_class(
                test_result_type
            )
        return None

    @staticmethod
    def _resolve_test_result_model_class(test_result_type: str) -> Any:
        from app.api.v1.modules.projects.model import (
            TestResult3DPrintModel,
            TestResultCoatingModel,
            TestResultCompositeModel,
            TestResultInkModel,
        )

        normalized = str(test_result_type or "").strip().lower()
        if normalized == "ink":
            return TestResultInkModel
        if normalized == "coating":
            return TestResultCoatingModel
        if normalized == "3dprint":
            return TestResult3DPrintModel
        if normalized == "composite":
            return TestResultCompositeModel
        return None

    @staticmethod
    def _primary_key_name(model_cls: Any) -> str:
        primary_key_columns = list(model_cls.__table__.primary_key.columns)
        if not primary_key_columns:
            raise ValidationException("Model has no primary key")
        return str(primary_key_columns[0].name)

    @staticmethod
    def _model_to_json_dict(model_obj: Any) -> dict[str, Any]:
        data: dict[str, Any] = {}
        for column in model_obj.__table__.columns:
            data[column.name] = AgentDbAdminService._to_json_safe(
                getattr(model_obj, column.name)
            )
        return data

    @staticmethod
    def _to_json_safe(value: Any) -> Any:
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, dict):
            return {
                str(key): AgentDbAdminService._to_json_safe(item)
                for key, item in value.items()
            }
        if isinstance(value, list):
            return [AgentDbAdminService._to_json_safe(item) for item in value]
        return value

    @staticmethod
    async def _rollback_from_snapshot(
        db: AsyncSession,
        *,
        plan: dict[str, Any],
        rollback_snapshot: dict[str, Any],
        execution_result: dict[str, Any],
    ) -> bool:
        try:
            normalized = AgentDbAdminService._normalize_plan(plan)
            domain = str(normalized.get("domain") or "")
            action = str(normalized.get("action") or "")
            test_result_type = str(normalized.get("test_result_type") or "")

            if action == "create":
                model_cls = AgentDbAdminService._resolve_model_class(
                    domain, test_result_type
                )
                if model_cls is None:
                    return False
                primary_key_name = AgentDbAdminService._primary_key_name(model_cls)
                created_ids = AgentDbAdminService._extract_created_ids_from_result(
                    execution_result,
                    primary_key_name,
                )
                deleted = False
                for created_id in created_ids:
                    obj = await db.get(model_cls, created_id)
                    if obj is None:
                        continue
                    await db.delete(obj)
                    deleted = True
                if deleted:
                    await db.commit()
                return deleted

            records = rollback_snapshot.get("records")
            if not isinstance(records, list) or not records:
                return False

            model_cls = AgentDbAdminService._resolve_model_class(
                domain, test_result_type
            )
            if model_cls is None:
                return False
            pk_name = AgentDbAdminService._primary_key_name(model_cls)

            restored = False
            for row in records:
                if not isinstance(row, dict):
                    continue
                record_data = AgentDbAdminService._deserialize_record_for_model(
                    model_cls,
                    row,
                )
                pk_value = record_data.get(pk_name)
                if pk_value is None:
                    continue

                existing = await db.get(model_cls, pk_value)
                if existing is None:
                    db.add(model_cls(**record_data))
                    restored = True
                    continue

                for key, value in record_data.items():
                    if key == pk_name:
                        continue
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                        restored = True

            if restored:
                await db.commit()
            return restored
        except Exception as exc:  # noqa: BLE001
            await db.rollback()
            logger.error(
                "Rollback snapshot restore failed: %s: %s", type(exc).__name__, exc
            )
            return False

    @staticmethod
    def _deserialize_record_for_model(
        model_cls: Any, row: dict[str, Any]
    ) -> dict[str, Any]:
        parsed: dict[str, Any] = {}
        for column in model_cls.__table__.columns:
            if column.name not in row:
                continue
            parsed[column.name] = AgentDbAdminService._deserialize_value_for_column(
                column.type,
                row[column.name],
            )
        return parsed

    @staticmethod
    def _deserialize_value_for_column(column_type: Any, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(column_type, DateTime):
            if isinstance(value, datetime):
                return value
            if isinstance(value, str):
                try:
                    return datetime.fromisoformat(value)
                except ValueError:
                    return value
        if isinstance(column_type, Date):
            if isinstance(value, date):
                return value
            if isinstance(value, str):
                try:
                    return date.fromisoformat(value)
                except ValueError:
                    return value
        return value

    @staticmethod
    def _extract_created_ids_from_result(
        execution_result: dict[str, Any],
        primary_key_name: str,
    ) -> list[int]:
        ids: list[int] = []
        if "created_id" in execution_result:
            try:
                ids.append(int(execution_result["created_id"]))
            except Exception:  # noqa: BLE001
                pass
        if "created_ids" in execution_result and isinstance(
            execution_result["created_ids"],
            list,
        ):
            for item in execution_result["created_ids"]:
                try:
                    ids.append(int(item))
                except Exception:  # noqa: BLE001
                    continue

        result_payload = execution_result.get("result")
        if isinstance(result_payload, dict):
            candidate_keys = [
                primary_key_name,
                primary_key_name.lower(),
            ]
            for key in candidate_keys:
                if key not in result_payload:
                    continue
                try:
                    ids.append(int(result_payload[key]))
                except Exception:  # noqa: BLE001
                    continue

        normalized_ids = sorted({item for item in ids if item > 0})
        return normalized_ids

    @staticmethod
    def _get_test_result_project_id(
        payload: dict[str, Any], target_id: Any
    ) -> int | None:
        project_id = AgentDbAdminService._pick_int(
            payload,
            "project_id",
            "ProjectID",
            "ProjectID_FK",
        )
        if project_id is not None:
            return project_id
        return AgentDbAdminService._pick_int({"target_id": target_id}, "target_id")

    @staticmethod
    async def _execute_change_plan(
        db: AsyncSession,
        plan: dict[str, Any],
        *,
        operator_user_id: int,
        operator_role: str,
    ) -> dict[str, Any]:
        _ = operator_user_id
        plan = AgentDbAdminService._normalize_plan(plan)
        intent = str(plan.get("intent") or "")
        domain = str(plan.get("domain") or "").lower()
        action = str(plan.get("action") or "").lower()
        raw_payload = plan.get("payload")
        payload: dict[str, Any] = raw_payload if isinstance(raw_payload, dict) else {}
        target_id = plan.get("target_id")
        raw_batch_ids = plan.get("batch_ids")
        batch_ids: list[Any] = raw_batch_ids if isinstance(raw_batch_ids, list) else []

        if intent == "admin_ops" or domain == "database" or action == "ddl":
            auth_cfg = get_agent_authorization_config()
            if not auth_cfg.can_admin(operator_role):
                raise ValidationException(
                    "Only admin roles can execute database-level admin operations"
                )
            raise ValidationException(
                "DDL/admin operations are currently plan-only. Please execute through controlled migration pipeline"
            )

        if domain == "materials":
            return await AgentDbAdminService._execute_material_change(
                db,
                action=action,
                payload=payload,
                target_id=target_id,
                batch_ids=batch_ids,
            )

        if domain == "fillers":
            return await AgentDbAdminService._execute_filler_change(
                db,
                action=action,
                payload=payload,
                target_id=target_id,
                batch_ids=batch_ids,
            )

        if domain == "projects":
            return await AgentDbAdminService._execute_project_change(
                db,
                action=action,
                payload=payload,
                target_id=target_id,
                batch_ids=batch_ids,
            )

        if domain == "compositions":
            return await AgentDbAdminService._execute_composition_change(
                db,
                action=action,
                payload=payload,
                target_id=target_id,
            )

        if domain == "test_results":
            return await AgentDbAdminService._execute_test_result_change(
                db,
                action=action,
                payload=payload,
                target_id=target_id,
                test_result_type=str(plan.get("test_result_type") or "").lower(),
            )

        raise ValidationException(f"Unsupported domain in plan: {domain}")

    @staticmethod
    async def _execute_material_change(
        db: AsyncSession,
        *,
        action: str,
        payload: dict[str, Any],
        target_id: Any,
        batch_ids: list[Any],
    ) -> dict[str, Any]:
        from app.api.v1.modules.materials.schema import (
            BatchDeleteRequest,
            MaterialCreateRequest,
            MaterialUpdateRequest,
        )
        from app.api.v1.modules.materials.service import MaterialService

        if action == "create":
            req = MaterialCreateRequest(
                **AgentDbAdminService._normalize_material_payload(payload)
            )
            obj = await MaterialService.create_material(db, req)
            return {
                "domain": "materials",
                "action": action,
                "result": obj.model_dump(mode="json"),
            }

        if action == "update":
            material_id = AgentDbAdminService._require_positive_int(
                target_id, "target_id"
            )
            req = MaterialUpdateRequest(
                **AgentDbAdminService._normalize_material_payload(payload)
            )
            obj = await MaterialService.update_material(db, material_id, req)
            return {
                "domain": "materials",
                "action": action,
                "result": obj.model_dump(mode="json"),
            }

        if action == "delete":
            material_id = AgentDbAdminService._require_positive_int(
                target_id, "target_id"
            )
            await MaterialService.delete_material(db, material_id)
            return {"domain": "materials", "action": action, "deleted_id": material_id}

        if action == "batch_delete":
            ids = AgentDbAdminService._normalize_batch_ids(batch_ids)
            req = BatchDeleteRequest(ids=ids)
            count = await MaterialService.batch_delete_materials(db, req)
            return {"domain": "materials", "action": action, "deleted_count": count}

        raise ValidationException(f"Unsupported materials action: {action}")

    @staticmethod
    async def _execute_filler_change(
        db: AsyncSession,
        *,
        action: str,
        payload: dict[str, Any],
        target_id: Any,
        batch_ids: list[Any],
    ) -> dict[str, Any]:
        from app.api.v1.modules.fillers.schema import (
            BatchDeleteRequest,
            FillerCreateRequest,
            FillerUpdateRequest,
        )
        from app.api.v1.modules.fillers.service import FillerService

        if action == "create":
            req = FillerCreateRequest(
                **AgentDbAdminService._normalize_filler_payload(payload)
            )
            obj = await FillerService.create_filler(db, req)
            return {
                "domain": "fillers",
                "action": action,
                "result": obj.model_dump(mode="json"),
            }

        if action == "update":
            filler_id = AgentDbAdminService._require_positive_int(
                target_id, "target_id"
            )
            req = FillerUpdateRequest(
                **AgentDbAdminService._normalize_filler_payload(payload)
            )
            obj = await FillerService.update_filler(db, filler_id, req)
            return {
                "domain": "fillers",
                "action": action,
                "result": obj.model_dump(mode="json"),
            }

        if action == "delete":
            filler_id = AgentDbAdminService._require_positive_int(
                target_id, "target_id"
            )
            await FillerService.delete_filler(db, filler_id)
            return {"domain": "fillers", "action": action, "deleted_id": filler_id}

        if action == "batch_delete":
            ids = AgentDbAdminService._normalize_batch_ids(batch_ids)
            req = BatchDeleteRequest(ids=ids)
            count = await FillerService.batch_delete_fillers(db, req)
            return {"domain": "fillers", "action": action, "deleted_count": count}

        raise ValidationException(f"Unsupported fillers action: {action}")

    @staticmethod
    async def _execute_project_change(
        db: AsyncSession,
        *,
        action: str,
        payload: dict[str, Any],
        target_id: Any,
        batch_ids: list[Any],
    ) -> dict[str, Any]:
        from app.api.v1.modules.projects.schema import (
            BatchDeleteRequest,
            ProjectCreateRequest,
            ProjectUpdateRequest,
        )
        from app.api.v1.modules.projects.service import ProjectService

        if action == "create":
            req = ProjectCreateRequest(
                **AgentDbAdminService._normalize_project_payload(payload)
            )
            obj = await ProjectService.create_project(db, req)
            return {
                "domain": "projects",
                "action": action,
                "result": obj.model_dump(mode="json"),
            }

        if action == "update":
            project_id = AgentDbAdminService._require_positive_int(
                target_id, "target_id"
            )
            req = ProjectUpdateRequest(
                **AgentDbAdminService._normalize_project_payload(payload)
            )
            obj = await ProjectService.update_project(db, project_id, req)
            return {
                "domain": "projects",
                "action": action,
                "result": obj.model_dump(mode="json"),
            }

        if action == "delete":
            project_id = AgentDbAdminService._require_positive_int(
                target_id, "target_id"
            )
            await ProjectService.delete_project(db, project_id)
            return {"domain": "projects", "action": action, "deleted_id": project_id}

        if action == "batch_delete":
            ids = AgentDbAdminService._normalize_batch_ids(batch_ids)
            req = BatchDeleteRequest(ids=ids)
            count = await ProjectService.batch_delete_projects(db, req)
            return {"domain": "projects", "action": action, "deleted_count": count}

        raise ValidationException(f"Unsupported projects action: {action}")

    @staticmethod
    async def _execute_composition_change(
        db: AsyncSession,
        *,
        action: str,
        payload: dict[str, Any],
        target_id: Any,
    ) -> dict[str, Any]:
        from app.api.v1.modules.projects.schema import (
            CompositionCreateRequest,
            CompositionUpdateRequest,
        )
        from app.api.v1.modules.projects.service import CompositionService

        if action == "create":
            req = CompositionCreateRequest(
                **AgentDbAdminService._normalize_composition_payload(payload)
            )
            obj = await CompositionService.create_composition(db, req)
            return {
                "domain": "compositions",
                "action": action,
                "result": obj.model_dump(mode="json"),
            }

        if action == "update":
            composition_id = AgentDbAdminService._require_positive_int(
                target_id, "target_id"
            )
            req = CompositionUpdateRequest(
                **AgentDbAdminService._normalize_composition_payload(payload)
            )
            obj = await CompositionService.update_composition(db, composition_id, req)
            return {
                "domain": "compositions",
                "action": action,
                "result": obj.model_dump(mode="json"),
            }

        if action == "delete":
            composition_id = AgentDbAdminService._require_positive_int(
                target_id, "target_id"
            )
            await CompositionService.delete_composition(db, composition_id)
            return {
                "domain": "compositions",
                "action": action,
                "deleted_id": composition_id,
            }

        raise ValidationException(f"Unsupported compositions action: {action}")

    @staticmethod
    async def _execute_test_result_change(
        db: AsyncSession,
        *,
        action: str,
        payload: dict[str, Any],
        target_id: Any,
        test_result_type: str,
    ) -> dict[str, Any]:
        from app.api.v1.modules.test_results.schema import (
            TestResult3DPrintRequest,
            TestResultCoatingRequest,
            TestResultCompositeRequest,
            TestResultInkRequest,
        )
        from app.api.v1.modules.test_results.service import TestResultService

        if action not in {"create", "update", "upsert"}:
            raise ValidationException(
                "test_results only supports create/update/upsert in admin agent"
            )

        normalized_payload = AgentDbAdminService._normalize_test_result_payload(payload)
        project_id = normalized_payload.pop("project_id", None)
        if project_id is None:
            project_id = target_id
        project_id = AgentDbAdminService._require_positive_int(project_id, "project_id")

        if test_result_type == "ink":
            req = TestResultInkRequest(**normalized_payload)
            obj = await TestResultService.create_or_update_ink_result(
                db, project_id, req
            )
        elif test_result_type == "coating":
            req = TestResultCoatingRequest(**normalized_payload)
            obj = await TestResultService.create_or_update_coating_result(
                db, project_id, req
            )
        elif test_result_type == "3dprint":
            req = TestResult3DPrintRequest(**normalized_payload)
            obj = await TestResultService.create_or_update_3dprint_result(
                db, project_id, req
            )
        elif test_result_type == "composite":
            req = TestResultCompositeRequest(**normalized_payload)
            obj = await TestResultService.create_or_update_composite_result(
                db, project_id, req
            )
        else:
            raise ValidationException(
                "test_result_type must be one of: ink, coating, 3dprint, composite"
            )

        return {
            "domain": "test_results",
            "action": action,
            "test_result_type": test_result_type,
            "result": obj.model_dump(mode="json"),
        }

    @staticmethod
    def _normalize_plan(plan: dict[str, Any]) -> dict[str, Any]:
        normalized: dict[str, Any] = {}
        normalized["intent"] = str(plan.get("intent") or "clarify").strip().lower()
        normalized["domain"] = str(plan.get("domain") or "").strip().lower()
        normalized["action"] = str(plan.get("action") or "").strip().lower()
        normalized["summary"] = str(plan.get("summary") or "").strip()
        normalized["risk_level"] = (
            str(plan.get("risk_level") or "medium").strip().lower()
        )
        normalized["reason"] = str(plan.get("reason") or "").strip()
        normalized["test_result_type"] = (
            str(plan.get("test_result_type") or "").strip().lower()
        )

        target_id = plan.get("target_id")
        normalized["target_id"] = target_id

        payload = plan.get("payload")
        normalized["payload"] = payload if isinstance(payload, dict) else {}

        batch_ids = plan.get("batch_ids")
        normalized["batch_ids"] = batch_ids if isinstance(batch_ids, list) else []
        return normalized

    @staticmethod
    def _normalize_material_payload(payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "trade_name": AgentDbAdminService._pick(
                payload,
                "trade_name",
                "TradeName",
                "name",
                "material_name",
            ),
            "category_fk": AgentDbAdminService._pick_int(
                payload,
                "category_fk",
                "Category_FK",
                "category_id",
            ),
            "supplier": AgentDbAdminService._pick(
                payload,
                "supplier",
                "Supplier",
            ),
            "cas_number": AgentDbAdminService._pick(
                payload,
                "cas_number",
                "CAS_Number",
                "cas",
            ),
            "density": AgentDbAdminService._pick(
                payload,
                "density",
                "Density",
            ),
            "viscosity": AgentDbAdminService._pick(
                payload,
                "viscosity",
                "Viscosity",
            ),
            "function_description": AgentDbAdminService._pick(
                payload,
                "function_description",
                "FunctionDescription",
                "function",
            ),
        }

    @staticmethod
    def _normalize_filler_payload(payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "trade_name": AgentDbAdminService._pick(
                payload,
                "trade_name",
                "TradeName",
                "name",
            ),
            "filler_type_fk": AgentDbAdminService._pick_int(
                payload,
                "filler_type_fk",
                "FillerType_FK",
                "filler_type_id",
            ),
            "supplier": AgentDbAdminService._pick(payload, "supplier", "Supplier"),
            "particle_size": AgentDbAdminService._pick(
                payload,
                "particle_size",
                "ParticleSize",
            ),
            "is_silanized": AgentDbAdminService._pick_int(
                payload,
                "is_silanized",
                "IsSilanized",
            ),
            "coupling_agent": AgentDbAdminService._pick(
                payload,
                "coupling_agent",
                "CouplingAgent",
            ),
            "surface_area": AgentDbAdminService._pick(
                payload,
                "surface_area",
                "SurfaceArea",
            ),
        }

    @staticmethod
    def _normalize_project_payload(payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "project_name": AgentDbAdminService._pick(
                payload,
                "project_name",
                "ProjectName",
                "name",
            ),
            "project_type_fk": AgentDbAdminService._pick_int(
                payload,
                "project_type_fk",
                "ProjectType_FK",
                "type_id",
            ),
            "substrate_application": AgentDbAdminService._pick(
                payload,
                "substrate_application",
                "SubstrateApplication",
            ),
            "formulator_name": AgentDbAdminService._pick(
                payload,
                "formulator_name",
                "FormulatorName",
            ),
            "formulation_date": AgentDbAdminService._pick(
                payload,
                "formulation_date",
                "FormulationDate",
            ),
        }

    @staticmethod
    def _normalize_composition_payload(payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "project_id": AgentDbAdminService._pick_int(
                payload,
                "project_id",
                "ProjectID",
                "ProjectID_FK",
            ),
            "material_id": AgentDbAdminService._pick_int(
                payload,
                "material_id",
                "MaterialID",
                "MaterialID_FK",
            ),
            "filler_id": AgentDbAdminService._pick_int(
                payload,
                "filler_id",
                "FillerID",
                "FillerID_FK",
            ),
            "weight_percentage": AgentDbAdminService._pick(
                payload,
                "weight_percentage",
                "WeightPercentage",
            ),
            "addition_method": AgentDbAdminService._pick(
                payload,
                "addition_method",
                "AdditionMethod",
            ),
            "remarks": AgentDbAdminService._pick(payload, "remarks", "Remarks"),
        }

    @staticmethod
    def _normalize_test_result_payload(payload: dict[str, Any]) -> dict[str, Any]:
        normalized: dict[str, Any] = {}
        for key, value in payload.items():
            normalized[key] = value

        project_id = AgentDbAdminService._pick_int(
            payload,
            "project_id",
            "ProjectID",
            "ProjectID_FK",
        )
        if project_id is not None:
            normalized["project_id"] = project_id

        return normalized

    @staticmethod
    def _safe_parse_json(raw: str) -> dict[str, Any] | None:
        text = (raw or "").strip()
        if not text:
            return None
        try:
            parsed = json.loads(text)
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            matched = re.search(r"\{[\s\S]*\}", text)
            if not matched:
                return None
            try:
                parsed = json.loads(matched.group(0))
                return parsed if isinstance(parsed, dict) else None
            except json.JSONDecodeError:
                return None

    @staticmethod
    def _keyword_plan_fallback(message: str) -> dict[str, Any] | None:
        lowered = (message or "").lower()
        action = ""
        if any(word in lowered for word in ["create", "add", "new", "insert"]):
            action = "create"
        elif any(word in lowered for word in ["edit", "update", "change", "modify"]):
            action = "update"
        elif any(word in lowered for word in ["remove", "delete"]):
            action = "delete"

        domain = ""
        if any(word in lowered for word in ["material", "materials", "raw material"]):
            domain = "materials"
        elif any(word in lowered for word in ["filler", "fillers"]):
            domain = "fillers"
        elif any(word in lowered for word in ["project", "projects"]):
            domain = "projects"
        elif any(word in lowered for word in ["composition", "compositions"]):
            domain = "compositions"
        elif any(word in lowered for word in ["test result", "test_results"]):
            domain = "test_results"
        elif any(word in lowered for word in ["schema", "index", "ddl", "grant"]):
            domain = "database"
            action = "ddl"

        if not domain or not action:
            return None

        return {
            "intent": "admin_ops" if domain == "database" else "mutate_domain",
            "domain": domain,
            "action": action,
            "payload": {},
            "summary": "Parsed by keyword fallback",
            "risk_level": "medium",
        }

    @staticmethod
    def _pick(payload: dict[str, Any], *keys: str) -> Any:
        for key in keys:
            if key in payload and payload[key] is not None:
                return payload[key]
        return None

    @staticmethod
    def _pick_int(payload: dict[str, Any], *keys: str) -> int | None:
        value = AgentDbAdminService._pick(payload, *keys)
        if value in (None, ""):
            return None
        try:
            return int(value)
        except Exception:  # noqa: BLE001
            return None

    @staticmethod
    def _require_positive_int(value: Any, field_name: str) -> int:
        try:
            parsed = int(value)
        except Exception as exc:  # noqa: BLE001
            raise ValidationException(
                f"{field_name} must be a positive integer"
            ) from exc
        if parsed <= 0:
            raise ValidationException(f"{field_name} must be a positive integer")
        return parsed

    @staticmethod
    def _normalize_batch_ids(batch_ids: list[Any]) -> list[int]:
        from app.config.settings import settings

        parsed: list[int] = []
        for item in batch_ids:
            try:
                value = int(item)
            except Exception:  # noqa: BLE001
                continue
            if value > 0:
                parsed.append(value)

        parsed = sorted(set(parsed))
        if not parsed:
            raise ValidationException(
                "batch_ids must contain at least one positive integer"
            )
        if len(parsed) > settings.AGENT_MUTATION_MAX_BATCH_SIZE:
            raise ValidationException(
                "batch_ids exceed AGENT_MUTATION_MAX_BATCH_SIZE "
                f"({settings.AGENT_MUTATION_MAX_BATCH_SIZE})"
            )
        return parsed
