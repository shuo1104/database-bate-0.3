"""Text-to-SQL orchestration service."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any, Protocol

from openai import OpenAI

from app.agent.config import get_agent_sql_config, get_deepseek_config
from app.agent.schemas import QueryRequestSchema, QueryResponseSchema
from app.agent.tools.sql.executor import SqlExecutionResult, SqlReadonlyExecutor
from app.agent.tools.sql.guard import SqlSafetyGuard
from app.agent.tools.sql.prompting import (
    build_sql_generation_prompts,
    extract_sql_from_llm_output,
)
from app.agent.tools.sql.schema_grounding import (
    build_schema_grounding_snapshot,
    get_effective_allowlist_tables,
    render_schema_grounding,
)
from app.core.custom_exceptions import (
    DatabaseException,
    ExternalServiceException,
    ValidationException,
)

SqlGenerator = Callable[
    [str, str, int, str | None, str | None],
    Awaitable[str],
]


class SqlExecutorProtocol(Protocol):
    async def fetch_sample_rows(
        self,
        table_names: list[str],
    ) -> dict[str, dict[str, Any]]: ...

    async def execute(
        self,
        sql: str,
        *,
        top_k: int,
        project_scope: list[int] | None = None,
    ) -> SqlExecutionResult: ...


class TextToSqlService:
    """Generate, validate, and execute SQL from natural language."""

    def __init__(
        self,
        *,
        executor: SqlExecutorProtocol | None = None,
        guard: SqlSafetyGuard | None = None,
        sql_generator: SqlGenerator | None = None,
    ) -> None:
        self._sql_cfg = get_agent_sql_config()
        self._allowlist_tables = (
            list(self._sql_cfg.allowlist_tables)
            if self._sql_cfg.allowlist_tables
            else get_effective_allowlist_tables()
        )
        self._executor = executor or SqlReadonlyExecutor(
            timeout_seconds=self._sql_cfg.timeout_seconds
        )
        self._guard = guard or SqlSafetyGuard(
            allowlist_tables=self._allowlist_tables,
            max_subquery_depth=2,
            max_union_count=3,
            require_where=True,
        )
        self._sql_generator = sql_generator

    async def run_query(self, request: QueryRequestSchema) -> QueryResponseSchema:
        top_k = max(1, min(int(request.top_k), 1000))
        snapshot = await build_schema_grounding_snapshot(
            sample_provider=self._executor.fetch_sample_rows,
            table_names=self._allowlist_tables,
        )
        schema_grounding_text = render_schema_grounding(snapshot)

        retry_count = 0
        previous_sql: str | None = None
        previous_error: str | None = None

        while retry_count <= self._sql_cfg.max_retries:
            generated_sql = await self._generate_sql(
                question=request.question,
                schema_grounding_text=schema_grounding_text,
                top_k=top_k,
                project_scope=request.project_scope,
                previous_sql=previous_sql,
                previous_error=previous_error,
            )

            try:
                checked_sql = self._guard.validate(generated_sql)
                execution = await self._executor.execute(
                    checked_sql,
                    top_k=top_k,
                    project_scope=request.project_scope,
                )
                formatted_text = self._format_result_table(
                    execution.columns,
                    execution.rows,
                )

                warning = previous_error if retry_count > 0 else None
                return QueryResponseSchema(
                    sql=checked_sql,
                    columns=execution.columns,
                    rows=execution.rows,
                    row_count=execution.row_count,
                    retries=retry_count,
                    warning=warning,
                    duration_ms=execution.duration_ms,
                    formatted_text=formatted_text,
                )
            except (ValidationException, DatabaseException) as exc:
                if retry_count >= self._sql_cfg.max_retries:
                    raise
                previous_sql = generated_sql
                previous_error = f"{type(exc).__name__}: {exc}"
                retry_count += 1

        raise DatabaseException("Text-to-SQL failed after retry loop")

    async def _generate_sql(
        self,
        *,
        question: str,
        schema_grounding_text: str,
        top_k: int,
        project_scope: list[int] | None,
        previous_sql: str | None,
        previous_error: str | None,
    ) -> str:
        if self._sql_generator is not None:
            return await self._sql_generator(
                question,
                schema_grounding_text,
                top_k,
                previous_sql,
                previous_error,
            )
        return await self._generate_sql_with_deepseek(
            question=question,
            schema_grounding_text=schema_grounding_text,
            top_k=top_k,
            project_scope=project_scope,
            previous_sql=previous_sql,
            previous_error=previous_error,
        )

    async def _generate_sql_with_deepseek(
        self,
        *,
        question: str,
        schema_grounding_text: str,
        top_k: int,
        project_scope: list[int] | None,
        previous_sql: str | None,
        previous_error: str | None,
    ) -> str:
        llm_cfg = get_deepseek_config()
        if not llm_cfg.api_key:
            raise ExternalServiceException("Deepseek", "DEEPSEEK_API_KEY is empty")

        system_prompt, user_prompt = build_sql_generation_prompts(
            question=question,
            schema_grounding_text=schema_grounding_text,
            top_k=top_k,
            project_scope=project_scope,
            previous_sql=previous_sql,
            previous_error=previous_error,
        )

        client = OpenAI(api_key=llm_cfg.api_key, base_url=llm_cfg.base_url)

        def _invoke_llm() -> str:
            response = client.chat.completions.create(
                model=llm_cfg.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=llm_cfg.temperature,
                max_tokens=llm_cfg.max_tokens,
            )
            return response.choices[0].message.content or ""

        raw_content = await asyncio.to_thread(_invoke_llm)
        extracted_sql = extract_sql_from_llm_output(raw_content)
        if not extracted_sql:
            raise ValidationException("LLM returned empty SQL")
        return extracted_sql

    @staticmethod
    def _format_result_table(columns: list[str], rows: list[dict[str, Any]]) -> str:
        if not columns:
            return (
                "| result |\n"
                "| --- |\n"
                "| (no columns) |\n\n"
                "No structured columns were returned by the query."
            )

        visible_rows = rows[:20]
        escaped_columns = [
            TextToSqlService._escape_markdown_cell(item) for item in columns
        ]
        header = "| " + " | ".join(escaped_columns) + " |"
        separator = "| " + " | ".join(["---"] * len(columns)) + " |"

        body_lines: list[str] = []
        for row in visible_rows:
            cells = [
                TextToSqlService._escape_markdown_cell(row.get(column))
                for column in columns
            ]
            body_lines.append("| " + " | ".join(cells) + " |")

        if not body_lines:
            empty_cells = ["(no rows)"] + [""] * (len(columns) - 1)
            body_lines.append("| " + " | ".join(empty_cells) + " |")

        table_text = "\n".join([header, separator, *body_lines])

        total_rows = len(rows)
        if total_rows == 0:
            summary = "No rows matched the query."
        elif total_rows > len(visible_rows):
            summary = (
                f"Returned {total_rows} rows; showing first {len(visible_rows)} rows."
            )
        else:
            summary = f"Returned {total_rows} row(s)."

        return f"{table_text}\n\n{summary}"

    @staticmethod
    def _escape_markdown_cell(value: Any) -> str:
        if value is None:
            text = "NULL"
        else:
            text = str(value)
        text = text.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
        return text.replace("|", "\\|")
