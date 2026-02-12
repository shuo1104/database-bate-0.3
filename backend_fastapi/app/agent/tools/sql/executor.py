"""Readonly SQL executor with timeout and row serialization."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from time import perf_counter
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config.settings import settings
from app.core.custom_exceptions import DatabaseException
from app.core.logger import logger


@dataclass(frozen=True)
class SqlExecutionResult:
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    duration_ms: int


_readonly_engine: AsyncEngine | None = None


def get_readonly_async_engine() -> AsyncEngine:
    global _readonly_engine
    if _readonly_engine is None:
        _readonly_engine = create_async_engine(
            url=settings.AGENT_READONLY_ASYNC_DB_URI,
            echo=False,
            pool_pre_ping=settings.POOL_PRE_PING,
            pool_recycle=settings.POOL_RECYCLE,
            pool_size=settings.POOL_SIZE,
            max_overflow=settings.MAX_OVERFLOW,
            pool_timeout=settings.POOL_TIMEOUT,
            future=True,
        )
    return _readonly_engine


class SqlReadonlyExecutor:
    """Execute SQL in readonly connection context."""

    def __init__(self, *, timeout_seconds: int) -> None:
        self._timeout_seconds = timeout_seconds
        self._session_factory = async_sessionmaker(
            bind=get_readonly_async_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    async def execute(
        self,
        sql: str,
        *,
        top_k: int,
        project_scope: list[int] | None = None,
    ) -> SqlExecutionResult:
        bounded_sql = self._wrap_with_limit(sql, top_k)
        scoped_sql = self._apply_project_scope_filter(bounded_sql, project_scope)
        started_at = perf_counter()

        async with self._session_factory() as session:
            try:
                query_result = await asyncio.wait_for(
                    session.execute(text(scoped_sql)),
                    timeout=self._timeout_seconds,
                )
                rows = [
                    self._serialize_row(dict(row_mapping))
                    for row_mapping in query_result.mappings().all()
                ]
                columns = list(query_result.keys())
            except asyncio.TimeoutError as exc:
                raise DatabaseException(
                    f"Readonly SQL execution timed out in {self._timeout_seconds}s"
                ) from exc
            except Exception as exc:  # noqa: BLE001
                raise DatabaseException(
                    f"Readonly SQL execution failed: {type(exc).__name__}: {exc}"
                ) from exc

        elapsed_ms = int((perf_counter() - started_at) * 1000)
        return SqlExecutionResult(
            columns=columns,
            rows=rows,
            row_count=len(rows),
            duration_ms=elapsed_ms,
        )

    async def fetch_sample_rows(
        self,
        table_names: list[str],
    ) -> dict[str, dict[str, Any]]:
        samples: dict[str, dict[str, Any]] = {}

        async with self._session_factory() as session:
            for table_name in table_names:
                if not self._is_safe_table_name(table_name):
                    continue
                sql = f'SELECT * FROM "{table_name}" LIMIT 1'
                try:
                    result = await asyncio.wait_for(
                        session.execute(text(sql)),
                        timeout=self._timeout_seconds,
                    )
                    row = result.mappings().first()
                    if row is not None:
                        samples[table_name] = self._serialize_row(dict(row))
                except Exception as exc:  # noqa: BLE001
                    logger.warning(
                        "Failed to fetch sample row for table %s: %s: %s",
                        table_name,
                        type(exc).__name__,
                        exc,
                    )

        return samples

    @staticmethod
    def _wrap_with_limit(sql: str, top_k: int) -> str:
        bounded_rows = max(1, min(int(top_k), 1000))
        stripped_sql = (sql or "").strip().rstrip(";")
        return (
            f"SELECT * FROM ({stripped_sql}) AS agent_sql_result LIMIT {bounded_rows}"
        )

    @classmethod
    def _apply_project_scope_filter(
        cls,
        sql: str,
        project_scope: list[int] | None,
    ) -> str:
        scope_ids = cls._sanitize_project_scope(project_scope)
        if not scope_ids:
            return sql

        scope_text = ", ".join(str(item) for item in scope_ids)
        return (
            "SELECT * FROM ("
            f"{sql}"
            ") AS agent_scope_result "
            "WHERE (CASE "
            "WHEN (to_jsonb(agent_scope_result)->>'ProjectID') ~ '^[0-9]+$' "
            "THEN (to_jsonb(agent_scope_result)->>'ProjectID')::int "
            "WHEN (to_jsonb(agent_scope_result)->>'ProjectID_FK') ~ '^[0-9]+$' "
            "THEN (to_jsonb(agent_scope_result)->>'ProjectID_FK')::int "
            "ELSE NULL END) "
            f"IN ({scope_text})"
        )

    @staticmethod
    def _sanitize_project_scope(project_scope: list[int] | None) -> list[int]:
        if not project_scope:
            return []

        normalized = sorted({int(item) for item in project_scope if int(item) > 0})
        return normalized

    @staticmethod
    def _is_safe_table_name(table_name: str) -> bool:
        return table_name.replace("_", "").isalnum()

    @classmethod
    def _serialize_row(cls, row: dict[str, Any]) -> dict[str, Any]:
        return {key: cls._serialize_value(value) for key, value in row.items()}

    @staticmethod
    def _serialize_value(value: Any) -> Any:
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        return value
