"""Phase 4 unit tests for Agent chat service."""

from __future__ import annotations

import io
import unittest
from datetime import datetime
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock, patch

from fastapi import BackgroundTasks, UploadFile

from app.api.v1.modules.agent.schema import (
    AgentChatIntent,
    AgentChatMode,
    AgentChatRequest,
    AgentToolTrace,
    AgentTaskStatus,
    AgentTaskSubmitResponse,
)
from app.api.v1.modules.agent.service import AgentChatService
from app.core.custom_exceptions import ExternalServiceException


class _FakeDbSession:
    def __init__(self) -> None:
        self.commit_count = 0
        self.rollback_count = 0

    async def commit(self) -> None:
        self.commit_count += 1

    async def rollback(self) -> None:
        self.rollback_count += 1


class _AuditObject:
    def __init__(self, audit_id: int) -> None:
        self.AuditID = audit_id


class Phase4ChatServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_follow_up_when_scope_missing(self) -> None:
        db = cast(Any, _FakeDbSession())
        request = AgentChatRequest(
            message="query project statistics", project_scope=None, top_k=20
        )
        current_user = {"user_id": 2, "username": "user", "role": "user"}

        with patch(
            "app.api.v1.modules.agent.service.AgentCRUD.append_audit_log",
            new=AsyncMock(return_value=_AuditObject(101)),
        ):
            result = await AgentChatService.handle_chat(
                db=db,
                background_tasks=BackgroundTasks(),
                request=request,
                current_user=current_user,
                file=None,
            )

        self.assertEqual(result.mode, AgentChatMode.follow_up)
        self.assertIsNotNone(result.follow_up_question)
        self.assertEqual(result.audit_id, 101)

    async def test_ingest_chat_submits_task(self) -> None:
        db = cast(Any, _FakeDbSession())
        request = AgentChatRequest(
            message="please ingest this file", project_scope=None, top_k=20
        )
        current_user = {"user_id": 2, "username": "user", "role": "user"}
        upload = UploadFile(filename="sample.csv", file=io.BytesIO(b"a,b\n1,2\n"))

        mock_task = AgentTaskSubmitResponse(
            task_id=300,
            task_type="ingest",
            status=AgentTaskStatus.pending,
            file_name="sample.csv",
            file_path="/tmp/sample.csv",
            created_at=datetime.now(),
        )

        with (
            patch(
                "app.api.v1.modules.agent.service.AgentIngestService.submit_ingest_task",
                new=AsyncMock(return_value=mock_task),
            ),
            patch(
                "app.api.v1.modules.agent.service.AgentCRUD.append_audit_log",
                new=AsyncMock(return_value=_AuditObject(202)),
            ),
        ):
            result = await AgentChatService.handle_chat(
                db=db,
                background_tasks=BackgroundTasks(),
                request=request,
                current_user=current_user,
                file=upload,
            )

        self.assertEqual(result.mode, AgentChatMode.async_task)
        self.assertEqual(result.task_id, 300)
        self.assertEqual(result.audit_id, 202)
        self.assertEqual(result.tool_traces[0].tool_name, "agent_document_ingest")

    async def test_external_service_error_returns_degraded(self) -> None:
        db = cast(Any, _FakeDbSession())
        request = AgentChatRequest(message="hello", project_scope=None, top_k=20)
        current_user = {"user_id": 1, "username": "admin", "role": "admin"}

        with (
            patch(
                "app.api.v1.modules.agent.service.AgentChatService._run_react_chat",
                new=AsyncMock(side_effect=ExternalServiceException("Deepseek", "down")),
            ),
            patch(
                "app.api.v1.modules.agent.service.AgentCRUD.append_audit_log",
                new=AsyncMock(return_value=_AuditObject(303)),
            ),
        ):
            result = await AgentChatService.handle_chat(
                db=db,
                background_tasks=BackgroundTasks(),
                request=request,
                current_user=current_user,
                file=None,
            )

        self.assertTrue(result.degraded)
        self.assertTrue(result.retryable)
        self.assertEqual(result.mode, AgentChatMode.follow_up)
        self.assertEqual(result.audit_id, 303)

    async def test_mutation_chat_creates_plan_task(self) -> None:
        db = cast(Any, _FakeDbSession())
        request = AgentChatRequest(
            message="create a material record", project_scope=None, top_k=20
        )
        current_user = {"user_id": 1, "username": "admin", "role": "admin"}

        with (
            patch(
                "app.api.v1.modules.agent.service.AgentChatService._infer_intent",
                new=AsyncMock(return_value=AgentChatIntent.mutate_domain),
            ),
            patch(
                "app.api.v1.modules.agent.service.AgentDbAdminService.build_change_plan",
                new=AsyncMock(
                    return_value={
                        "intent": "mutate_domain",
                        "domain": "materials",
                        "action": "create",
                        "payload": {"trade_name": "Resin-X"},
                        "summary": "Create a material",
                    }
                ),
            ),
            patch(
                "app.api.v1.modules.agent.service.AgentDbAdminService.submit_change_plan_task",
                new=AsyncMock(return_value=501),
            ),
            patch(
                "app.api.v1.modules.agent.service.AgentCRUD.append_audit_log",
                new=AsyncMock(return_value=_AuditObject(401)),
            ),
        ):
            result = await AgentChatService.handle_chat(
                db=db,
                background_tasks=BackgroundTasks(),
                request=request,
                current_user=current_user,
                file=None,
            )

        self.assertEqual(result.mode, AgentChatMode.follow_up)
        self.assertEqual(result.intent, AgentChatIntent.mutate_domain)
        self.assertEqual(result.task_id, 501)
        self.assertIn("execute plan 501", result.reply)
        self.assertEqual(result.tool_traces[0].tool_name, "agent_db_change_planner")

    async def test_execute_plan_command_runs_db_admin_executor(self) -> None:
        db = cast(Any, _FakeDbSession())
        request = AgentChatRequest(
            message="execute plan 88", project_scope=None, top_k=20
        )
        current_user = {"user_id": 1, "username": "admin", "role": "admin"}

        with (
            patch(
                "app.api.v1.modules.agent.service.AgentDbAdminService.execute_plan_task",
                new=AsyncMock(return_value={"domain": "materials", "action": "create"}),
            ),
            patch(
                "app.api.v1.modules.agent.service.AgentCRUD.append_audit_log",
                new=AsyncMock(return_value=_AuditObject(402)),
            ),
        ):
            result = await AgentChatService.handle_chat(
                db=db,
                background_tasks=BackgroundTasks(),
                request=request,
                current_user=current_user,
                file=None,
            )

        self.assertEqual(result.mode, AgentChatMode.sync)
        self.assertEqual(result.intent, AgentChatIntent.mutate_domain)
        self.assertIsNotNone(result.query_result)
        query_result = result.query_result or {}
        self.assertEqual(query_result.get("plan_task_id"), 88)
        self.assertEqual(result.tool_traces[0].tool_name, "agent_db_change_executor")

    async def test_run_react_chat_uses_error_safe_reply_when_sql_tool_fails(
        self,
    ) -> None:
        request = AgentChatRequest(
            message="Output all project information in the database",
            project_scope=None,
            top_k=20,
        )

        class _FakeExecutor:
            async def ainvoke(
                self, *_args: object, **_kwargs: object
            ) -> dict[str, object]:
                return {
                    "messages": [
                        SimpleNamespace(
                            content=(
                                "Based on attempted queries, I found two records: "
                                "ada and STRAP."
                            )
                        )
                    ]
                }

        with (
            patch(
                "app.api.v1.modules.agent.service.build_react_agent",
                return_value=_FakeExecutor(),
            ),
            patch(
                "app.api.v1.modules.agent.service.AgentChatService._build_tool_traces",
                return_value=[
                    AgentToolTrace(
                        tool_name="agent_text_to_sql",
                        status="ok",
                        tool_output={
                            "ok": False,
                            "error": "DatabaseException: relation tbl_ProjectInfo does not exist",
                        },
                    )
                ],
            ),
        ):
            result = await AgentChatService._run_react_chat(
                request=request,
                intent=AgentChatIntent.query,
                user_role="admin",
                user_id=1,
            )

        self.assertEqual(result.mode, AgentChatMode.follow_up)
        self.assertTrue(result.degraded)
        self.assertTrue(result.retryable)
        self.assertIn("cannot provide record-level results", result.reply)
        self.assertNotIn("ada", result.reply.lower())
        self.assertNotIn("strap", result.reply.lower())
        self.assertIsNotNone(result.query_result)
        query_result = result.query_result or {}
        self.assertEqual(query_result.get("ok"), False)
        self.assertIn("tbl_ProjectInfo", str(query_result.get("error")))


if __name__ == "__main__":
    unittest.main()
