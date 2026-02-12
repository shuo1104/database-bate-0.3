"""Phase 4 unit tests for DB admin planning service."""

from __future__ import annotations

import unittest
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock, patch

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.modules.agent.db_admin import AgentDbAdminService
from app.core.custom_exceptions import ValidationException


class _FakeDbSession:
    def __init__(self) -> None:
        self.commit_count = 0
        self.rollback_count = 0
        self.refresh_count = 0

    async def commit(self) -> None:
        self.commit_count += 1

    async def rollback(self) -> None:
        self.rollback_count += 1

    async def refresh(self, _obj: object) -> None:
        self.refresh_count += 1


class _AuthAllowReview:
    def can_review(self, _role: str) -> bool:
        return True

    def can_mutate(self, _role: str) -> bool:
        return False


class _AuthAllowMutate:
    def can_review(self, _role: str) -> bool:
        return False

    def can_mutate(self, _role: str) -> bool:
        return True


class Phase4DbAdminServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_list_change_plan_tasks_uses_paginated_query_without_approval_filter(
        self,
    ) -> None:
        db = cast(AsyncSession, _FakeDbSession())

        with (
            patch(
                "app.api.v1.modules.agent.db_admin.AgentCRUD.get_tasks_paginated",
                new=AsyncMock(return_value=([], 0)),
            ) as mock_paginated,
            patch(
                "app.api.v1.modules.agent.db_admin.AgentCRUD.get_tasks_by_type",
                new=AsyncMock(return_value=[]),
            ) as mock_by_type,
        ):
            result = await AgentDbAdminService.list_change_plan_tasks(
                db,
                page=1,
                page_size=20,
                task_status="pending",
                approval_status=None,
            )

        self.assertEqual(result["total"], 0)
        self.assertEqual(result["items"], [])
        mock_paginated.assert_awaited_once()
        mock_by_type.assert_not_awaited()

    async def test_list_change_plan_tasks_filters_by_approval_status(self) -> None:
        db = cast(AsyncSession, _FakeDbSession())
        fake_tasks = [SimpleNamespace(TaskID=1), SimpleNamespace(TaskID=2)]

        with (
            patch(
                "app.api.v1.modules.agent.db_admin.AgentCRUD.get_tasks_by_type",
                new=AsyncMock(return_value=fake_tasks),
            ),
            patch(
                "app.api.v1.modules.agent.db_admin.AgentDbAdminService._build_plan_record",
                side_effect=[
                    {"task_id": 1, "approval_status": "pending"},
                    {"task_id": 2, "approval_status": "approved"},
                ],
            ),
        ):
            result = await AgentDbAdminService.list_change_plan_tasks(
                db,
                page=1,
                page_size=20,
                task_status=None,
                approval_status="approved",
            )

        self.assertEqual(result["total"], 1)
        self.assertEqual(result["items"][0]["task_id"], 2)

    async def test_approve_change_plan_task_rejects_second_review(self) -> None:
        db = cast(AsyncSession, _FakeDbSession())
        task = SimpleNamespace(
            TaskID=7,
            TaskType="db_change_plan",
            Status="pending",
            Payload={"approval": {"status": "approved"}},
        )

        with (
            patch(
                "app.api.v1.modules.agent.db_admin.get_agent_authorization_config",
                return_value=_AuthAllowReview(),
            ),
            patch(
                "app.api.v1.modules.agent.db_admin.AgentCRUD.get_task_by_id",
                new=AsyncMock(return_value=task),
            ),
        ):
            with self.assertRaises(ValidationException):
                await AgentDbAdminService.approve_change_plan_task(
                    db,
                    task_id=7,
                    action="approve",
                    approver_user_id=10,
                    approver_role="admin",
                    comment="ok",
                )

    async def test_approve_change_plan_task_returns_approver_role(self) -> None:
        db = cast(AsyncSession, _FakeDbSession())
        task = SimpleNamespace(
            TaskID=8,
            TaskType="db_change_plan",
            Status="pending",
            Payload={"approval": {"status": "pending"}},
        )

        with (
            patch(
                "app.api.v1.modules.agent.db_admin.get_agent_authorization_config",
                return_value=_AuthAllowReview(),
            ),
            patch(
                "app.api.v1.modules.agent.db_admin.AgentCRUD.get_task_by_id",
                new=AsyncMock(return_value=task),
            ),
            patch(
                "app.api.v1.modules.agent.db_admin.AgentCRUD.update_task",
                new=AsyncMock(return_value=task),
            ),
        ):
            result = await AgentDbAdminService.approve_change_plan_task(
                db,
                task_id=8,
                action="approve",
                approver_user_id=11,
                approver_role="reviewer",
                comment="approved",
            )

        self.assertEqual(result["approval_status"], "approved")
        self.assertEqual(result["approved_by_user_id"], 11)
        self.assertEqual(result["approved_by_role"], "reviewer")

    async def test_execute_plan_task_returns_executed_role(self) -> None:
        db = cast(AsyncSession, _FakeDbSession())
        task = SimpleNamespace(
            TaskID=9,
            TaskType="db_change_plan",
            Status="pending",
            Payload={
                "plan": {"intent": "mutate_domain", "domain": "materials"},
                "approval": {"status": "approved"},
                "rollback_snapshot": {"records": []},
            },
            Result=None,
            ErrorMessage=None,
        )

        with (
            patch(
                "app.api.v1.modules.agent.db_admin.get_agent_authorization_config",
                return_value=_AuthAllowMutate(),
            ),
            patch(
                "app.api.v1.modules.agent.db_admin.AgentCRUD.get_task_by_id",
                new=AsyncMock(return_value=task),
            ),
            patch(
                "app.api.v1.modules.agent.db_admin.AgentCRUD.update_task",
                new=AsyncMock(return_value=task),
            ),
            patch(
                "app.api.v1.modules.agent.db_admin.AgentDbAdminService._execute_change_plan",
                new=AsyncMock(return_value={"domain": "materials", "action": "create"}),
            ),
        ):
            result = await AgentDbAdminService.execute_plan_task(
                db,
                task_id=9,
                user_id=1,
                user_role="admin",
            )

        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(result["executed_by_user_id"], 1)
        self.assertEqual(result["executed_by_role"], "admin")

    async def test_execute_plan_task_marks_failed_with_rollback_flag_on_post_exec_error(
        self,
    ) -> None:
        db = cast(AsyncSession, _FakeDbSession())
        task = SimpleNamespace(
            TaskID=10,
            TaskType="db_change_plan",
            Status="pending",
            Payload={
                "plan": {"intent": "mutate_domain", "domain": "materials"},
                "approval": {"status": "approved"},
                "rollback_snapshot": {"records": [{"MaterialID": 1}]},
            },
            Result=None,
            ErrorMessage=None,
        )
        captured_failed_payload: dict[str, object] = {}

        async def _mock_update_task(
            _db: object,
            _task_obj: object,
            **kwargs: object,
        ) -> object:
            call_index = _mock_update_task.call_index
            _mock_update_task.call_index += 1
            if call_index == 0:
                return task
            if call_index == 1:
                raise RuntimeError("persist failed after execution")
            captured_failed_payload.update(kwargs)
            return task

        _mock_update_task.call_index = 0

        with (
            patch(
                "app.api.v1.modules.agent.db_admin.get_agent_authorization_config",
                return_value=_AuthAllowMutate(),
            ),
            patch(
                "app.api.v1.modules.agent.db_admin.AgentCRUD.get_task_by_id",
                new=AsyncMock(side_effect=[task, task]),
            ),
            patch(
                "app.api.v1.modules.agent.db_admin.AgentCRUD.update_task",
                new=AsyncMock(side_effect=_mock_update_task),
            ),
            patch(
                "app.api.v1.modules.agent.db_admin.AgentDbAdminService._execute_change_plan",
                new=AsyncMock(return_value={"domain": "materials", "action": "create"}),
            ),
            patch(
                "app.api.v1.modules.agent.db_admin.AgentDbAdminService._rollback_from_snapshot",
                new=AsyncMock(return_value=True),
            ) as mock_rollback,
        ):
            with self.assertRaises(RuntimeError):
                await AgentDbAdminService.execute_plan_task(
                    db,
                    task_id=10,
                    user_id=1,
                    user_role="admin",
                )

        mock_rollback.assert_awaited_once()
        payload = captured_failed_payload.get("payload")
        self.assertIsInstance(payload, dict)
        payload_dict = payload if isinstance(payload, dict) else {}
        self.assertTrue(payload_dict.get("rollback_performed"))
        self.assertEqual(captured_failed_payload.get("status"), "failed")


if __name__ == "__main__":
    unittest.main()
