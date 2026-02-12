"""Phase 1 controller tests for ingest/review endpoints."""

from __future__ import annotations

import json
import unittest
from datetime import datetime
from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

import app.api.v1.modules.agent.controller as agent_controller
from app.api.v1.modules.agent.schema import (
    AgentChatIntent,
    AgentChatMode,
    AgentChatResponse,
    AgentPlanApprovalStatus,
    AgentReviewDeleteResponse,
    AgentReviewListResponse,
    AgentReviewStatus,
    AgentReviewUpdateResponse,
    AgentTaskResponse,
    AgentTaskStatus,
    AgentTaskSubmitResponse,
)
from app.core.database import get_db
from app.core.security import create_access_token


class Phase1AgentControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        app = FastAPI()
        app.include_router(agent_controller.router, prefix="/api/v1/agent")

        async def fake_get_db():
            yield object()

        app.dependency_overrides[get_db] = fake_get_db
        self.app = app
        self.client = TestClient(app)
        self.user_token = create_access_token(
            {"user_id": 2, "username": "user", "role": "user"}
        )
        self.admin_token = create_access_token(
            {"user_id": 1, "username": "admin", "role": "admin"}
        )

    def tearDown(self) -> None:
        self.app.dependency_overrides.clear()

    def test_ingest_endpoint_returns_task_id(self) -> None:
        mock_response = AgentTaskSubmitResponse(
            task_id=101,
            task_type="ingest",
            status=AgentTaskStatus.pending,
            file_name="sample.csv",
            file_path="/tmp/sample.csv",
            created_at=datetime.now(),
        )

        with patch.object(
            agent_controller.AgentIngestService,
            "submit_ingest_task",
            new=AsyncMock(return_value=mock_response),
        ):
            response = self.client.post(
                "/api/v1/agent/ingest",
                files={"file": ("sample.csv", b"a,b\n1,2\n", "text/csv")},
                headers={"Authorization": f"Bearer {self.user_token}"},
            )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["data"]["task_id"], 101)

    def test_task_status_endpoint(self) -> None:
        mock_response = AgentTaskResponse(
            TaskID=101,
            TaskType="ingest",
            Status=AgentTaskStatus.succeeded,
            Payload={"source_file_name": "sample.csv"},
            Result={"record_id": 501},
            ErrorMessage=None,
            CreatedAt=datetime.now(),
            StartedAt=datetime.now(),
            FinishedAt=datetime.now(),
        )

        with patch.object(
            agent_controller.AgentIngestService,
            "get_task_status",
            new=AsyncMock(return_value=mock_response),
        ):
            response = self.client.get(
                "/api/v1/agent/tasks/101",
                headers={"Authorization": f"Bearer {self.user_token}"},
            )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["data"]["status"], AgentTaskStatus.succeeded.value)

    def test_review_list_endpoint_for_admin(self) -> None:
        mock_response = AgentReviewListResponse(
            items=[],
            total=0,
            page=1,
            page_size=20,
        )

        with patch.object(
            agent_controller.AgentIngestService,
            "list_review_records",
            new=AsyncMock(return_value=mock_response),
        ) as mock_list:
            response = self.client.get(
                "/api/v1/agent/review",
                headers={"Authorization": f"Bearer {self.admin_token}"},
            )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["data"]["total"], 0)
        mock_list.assert_awaited_once()
        self.assertIsNone(mock_list.await_args.kwargs.get("review_status"))

    def test_review_update_endpoint_for_admin(self) -> None:
        mock_response = AgentReviewUpdateResponse(
            record_id=9,
            review_status=AgentReviewStatus.approved,
            reviewed_by_user_id=1,
            reviewed_at=datetime.now(),
            task_id=101,
        )

        with patch.object(
            agent_controller.AgentIngestService,
            "review_record",
            new=AsyncMock(return_value=mock_response),
        ):
            response = self.client.put(
                "/api/v1/agent/review/9",
                json={"action": "approved", "comment": "looks good"},
                headers={"Authorization": f"Bearer {self.admin_token}"},
            )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["data"]["review_status"], "approved")

    def test_review_delete_endpoint_for_admin(self) -> None:
        mock_response = AgentReviewDeleteResponse(
            record_id=9,
            task_id=101,
            review_status=AgentReviewStatus.pending_review,
            deleted_at=datetime.now(),
        )

        with patch.object(
            agent_controller.AgentIngestService,
            "delete_review_record",
            new=AsyncMock(return_value=mock_response),
        ):
            response = self.client.delete(
                "/api/v1/agent/review/9",
                headers={"Authorization": f"Bearer {self.admin_token}"},
            )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["data"]["record_id"], 9)

    def test_chat_endpoint_sync_response(self) -> None:
        mock_response = AgentChatResponse(
            mode=AgentChatMode.sync,
            intent=AgentChatIntent.query,
            reply="query ok",
            query_result={"ok": True, "row_count": 1},
        )

        with patch.object(
            agent_controller.AgentChatService,
            "handle_chat",
            new=AsyncMock(return_value=mock_response),
        ):
            response = self.client.post(
                "/api/v1/agent/chat",
                data={
                    "message": "query projects",
                    "top_k": "50",
                    "project_scope": "[1,2]",
                },
                headers={"Authorization": f"Bearer {self.user_token}"},
            )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["data"]["mode"], "sync")
        self.assertEqual(body["data"]["intent"], "query")

    def test_chat_endpoint_with_file(self) -> None:
        mock_response = AgentChatResponse(
            mode=AgentChatMode.async_task,
            intent=AgentChatIntent.ingest,
            reply="task submitted",
            task_id=201,
        )

        with patch.object(
            agent_controller.AgentChatService,
            "handle_chat",
            new=AsyncMock(return_value=mock_response),
        ):
            response = self.client.post(
                "/api/v1/agent/chat",
                data={"message": "please parse this file", "top_k": "100"},
                files={"file": ("sample.csv", b"a,b\n1,2\n", "text/csv")},
                headers={"Authorization": f"Bearer {self.user_token}"},
            )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["data"]["mode"], "async_task")
        self.assertEqual(body["data"]["task_id"], 201)

    def test_chat_stream_endpoint(self) -> None:
        mock_response = AgentChatResponse(
            mode=AgentChatMode.sync,
            intent=AgentChatIntent.query,
            reply="streamed response text",
            query_result={"ok": True},
        )

        with patch.object(
            agent_controller.AgentChatService,
            "handle_chat",
            new=AsyncMock(return_value=mock_response),
        ):
            response = self.client.post(
                "/api/v1/agent/chat/stream",
                data={"message": "stream this reply", "top_k": "50"},
                headers={"Authorization": f"Bearer {self.user_token}"},
            )

        self.assertEqual(response.status_code, 200)

        lines = [line for line in response.text.splitlines() if line.strip()]
        payloads = [json.loads(line) for line in lines]

        self.assertGreaterEqual(len(payloads), 2)
        self.assertEqual(payloads[0]["type"], "start")
        self.assertEqual(payloads[-1]["type"], "done")
        self.assertEqual(payloads[-1]["response"]["reply"], "streamed response text")

    def test_change_plan_list_endpoint(self) -> None:
        mock_response = {
            "items": [
                {
                    "task_id": 501,
                    "task_status": "pending",
                    "approval_status": AgentPlanApprovalStatus.pending.value,
                }
            ],
            "total": 1,
            "page": 1,
            "page_size": 20,
        }

        with (
            patch.object(
                agent_controller.AgentIngestService,
                "_ensure_agent_role",
                return_value=None,
            ),
            patch.object(
                agent_controller.AgentDbAdminService,
                "list_change_plan_tasks",
                new=AsyncMock(return_value=mock_response),
            ),
        ):
            response = self.client.get(
                "/api/v1/agent/plans",
                headers={"Authorization": f"Bearer {self.admin_token}"},
            )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["data"]["total"], 1)
        self.assertEqual(body["data"]["items"][0]["task_id"], 501)

    def test_change_plan_approve_endpoint(self) -> None:
        mock_response = {
            "task_id": 501,
            "approval_status": AgentPlanApprovalStatus.approved.value,
            "approved_by_user_id": 1,
            "approved_by_role": "admin",
        }

        with patch.object(
            agent_controller.AgentDbAdminService,
            "approve_change_plan_task",
            new=AsyncMock(return_value=mock_response),
        ):
            response = self.client.post(
                "/api/v1/agent/plans/501/approve",
                json={"action": "approve", "comment": "ok"},
                headers={"Authorization": f"Bearer {self.admin_token}"},
            )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["data"]["task_id"], 501)
        self.assertEqual(body["data"]["approval_status"], "approved")

    def test_change_plan_execute_endpoint(self) -> None:
        mock_response = {
            "task_id": 501,
            "status": "succeeded",
            "executed_by_user_id": 1,
            "executed_by_role": "admin",
            "rollback_performed": False,
        }

        with patch.object(
            agent_controller.AgentDbAdminService,
            "execute_plan_task",
            new=AsyncMock(return_value=mock_response),
        ):
            response = self.client.post(
                "/api/v1/agent/plans/501/execute",
                headers={"Authorization": f"Bearer {self.admin_token}"},
            )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["data"]["task_id"], 501)
        self.assertEqual(body["data"]["status"], "succeeded")


if __name__ == "__main__":
    unittest.main()
