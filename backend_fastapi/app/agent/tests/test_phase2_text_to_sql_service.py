"""Phase 2 integration tests for Text-to-SQL service with mocked LLM."""

from __future__ import annotations

import unittest
from typing import Any

from app.agent.schemas import QueryRequestSchema
from app.agent.tools.sql.executor import SqlExecutionResult
from app.agent.tools.sql.service import TextToSqlService
from app.core.custom_exceptions import ValidationException


class _FakeExecutor:
    def __init__(self) -> None:
        self.executed_sql: list[str] = []

    async def fetch_sample_rows(
        self, table_names: list[str]
    ) -> dict[str, dict[str, Any]]:
        _ = table_names
        return {
            "tbl_ProjectInfo": {
                "ProjectID": 1,
                "ProjectName": "Demo Project",
            }
        }

    async def execute(
        self,
        sql: str,
        *,
        top_k: int,
        project_scope: list[int] | None = None,
    ) -> SqlExecutionResult:
        _ = top_k, project_scope
        self.executed_sql.append(sql)
        return SqlExecutionResult(
            columns=["ProjectID", "ProjectName"],
            rows=[{"ProjectID": 1, "ProjectName": "Demo Project"}],
            row_count=1,
            duration_ms=12,
        )


class _FakeEmptyExecutor(_FakeExecutor):
    async def execute(
        self,
        sql: str,
        *,
        top_k: int,
        project_scope: list[int] | None = None,
    ) -> SqlExecutionResult:
        _ = top_k, project_scope
        self.executed_sql.append(sql)
        return SqlExecutionResult(
            columns=["ProjectID", "ProjectName"],
            rows=[],
            row_count=0,
            duration_ms=7,
        )


class _FakeSpecialCellExecutor(_FakeExecutor):
    async def execute(
        self,
        sql: str,
        *,
        top_k: int,
        project_scope: list[int] | None = None,
    ) -> SqlExecutionResult:
        _ = top_k, project_scope
        self.executed_sql.append(sql)
        return SqlExecutionResult(
            columns=["ProjectID", "ProjectName"],
            rows=[{"ProjectID": 2, "ProjectName": "A|B\nC"}],
            row_count=1,
            duration_ms=9,
        )


class Phase2TextToSqlServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_service_executes_valid_sql(self) -> None:
        async def sql_generator(
            question: str,
            schema_grounding_text: str,
            top_k: int,
            previous_sql: str | None,
            previous_error: str | None,
        ) -> str:
            _ = question, schema_grounding_text, top_k, previous_sql, previous_error
            return (
                'SELECT "ProjectID", "ProjectName" '
                'FROM "tbl_ProjectInfo" '
                'WHERE "ProjectID" = 1'
            )

        fake_executor = _FakeExecutor()
        service = TextToSqlService(executor=fake_executor, sql_generator=sql_generator)

        result = await service.run_query(
            QueryRequestSchema(question="query projects", top_k=10)
        )

        self.assertEqual(result.row_count, 1)
        self.assertEqual(result.retries, 0)
        self.assertIn("ProjectID", result.columns)
        self.assertEqual(len(fake_executor.executed_sql), 1)
        self.assertIn("| ProjectID | ProjectName |", result.formatted_text)
        self.assertIn("Returned 1 row(s).", result.formatted_text)

    async def test_service_retries_after_guard_failure(self) -> None:
        call_count = 0

        async def sql_generator(
            question: str,
            schema_grounding_text: str,
            top_k: int,
            previous_sql: str | None,
            previous_error: str | None,
        ) -> str:
            nonlocal call_count
            _ = question, schema_grounding_text, top_k, previous_sql, previous_error
            call_count += 1
            if call_count == 1:
                return 'SELECT * FROM "tbl_Users" WHERE "UserID" = 1'
            return 'SELECT "ProjectID" FROM "tbl_ProjectInfo" WHERE "ProjectID" = 1'

        fake_executor = _FakeExecutor()
        service = TextToSqlService(executor=fake_executor, sql_generator=sql_generator)

        result = await service.run_query(
            QueryRequestSchema(question="query projects", top_k=10)
        )

        self.assertEqual(call_count, 2)
        self.assertEqual(result.retries, 1)
        self.assertEqual(result.row_count, 1)

    async def test_service_fails_after_retry_exhausted(self) -> None:
        async def sql_generator(
            question: str,
            schema_grounding_text: str,
            top_k: int,
            previous_sql: str | None,
            previous_error: str | None,
        ) -> str:
            _ = question, schema_grounding_text, top_k, previous_sql, previous_error
            return 'UPDATE "tbl_ProjectInfo" SET "ProjectName" = \'bad\''

        service = TextToSqlService(
            executor=_FakeExecutor(), sql_generator=sql_generator
        )

        with self.assertRaises(ValidationException):
            await service.run_query(
                QueryRequestSchema(question="update project", top_k=10)
            )

    async def test_service_formats_empty_result_as_table_with_description(self) -> None:
        async def sql_generator(
            question: str,
            schema_grounding_text: str,
            top_k: int,
            previous_sql: str | None,
            previous_error: str | None,
        ) -> str:
            _ = question, schema_grounding_text, top_k, previous_sql, previous_error
            return (
                'SELECT "ProjectID", "ProjectName" '
                'FROM "tbl_ProjectInfo" '
                'WHERE "ProjectID" = -1'
            )

        service = TextToSqlService(
            executor=_FakeEmptyExecutor(),
            sql_generator=sql_generator,
        )
        result = await service.run_query(
            QueryRequestSchema(question="query missing project", top_k=10)
        )

        self.assertEqual(result.row_count, 0)
        self.assertIn("| ProjectID | ProjectName |", result.formatted_text)
        self.assertIn("| (no rows) |  |", result.formatted_text)
        self.assertIn("No rows matched the query.", result.formatted_text)

    async def test_service_escapes_markdown_breaking_cells(self) -> None:
        async def sql_generator(
            question: str,
            schema_grounding_text: str,
            top_k: int,
            previous_sql: str | None,
            previous_error: str | None,
        ) -> str:
            _ = question, schema_grounding_text, top_k, previous_sql, previous_error
            return (
                'SELECT "ProjectID", "ProjectName" '
                'FROM "tbl_ProjectInfo" '
                'WHERE "ProjectID" = 2'
            )

        service = TextToSqlService(
            executor=_FakeSpecialCellExecutor(),
            sql_generator=sql_generator,
        )
        result = await service.run_query(QueryRequestSchema(question="query", top_k=10))

        self.assertIn("A\\|B C", result.formatted_text)
        self.assertIn("Returned 1 row(s).", result.formatted_text)


if __name__ == "__main__":
    unittest.main()
