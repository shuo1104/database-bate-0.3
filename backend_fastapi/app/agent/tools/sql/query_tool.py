"""LangChain tool wrapper for Text-to-SQL."""

from __future__ import annotations

import json

from langchain_core.tools import tool

from app.agent.core.request_context import get_agent_request_context
from app.agent.schemas import QueryRequestSchema
from app.agent.tools.sql.service import TextToSqlService


def _parse_project_scope(project_scope: str) -> list[int] | None:
    raw_scope = (project_scope or "").strip()
    if not raw_scope:
        return None

    try:
        decoded = json.loads(raw_scope)
        if isinstance(decoded, list):
            return [int(item) for item in decoded]
    except Exception:  # noqa: BLE001
        pass

    values = []
    for chunk in raw_scope.split(","):
        piece = chunk.strip()
        if not piece:
            continue
        values.append(int(piece))
    return values or None


@tool("agent_text_to_sql")
async def agent_text_to_sql(
    question: str,
    top_k: int = 100,
    project_scope: str = "",
) -> str:
    """Convert natural language query into safe SQL and execute it."""

    service = TextToSqlService()
    request_context = get_agent_request_context()

    parsed_scope = _parse_project_scope(project_scope)
    effective_scope = parsed_scope
    effective_top_k = top_k
    if request_context is not None:
        if request_context.project_scope is not None:
            effective_scope = request_context.project_scope
        try:
            effective_top_k = min(int(top_k), int(request_context.top_k))
        except Exception:  # noqa: BLE001
            effective_top_k = top_k

    try:
        request = QueryRequestSchema(
            question=question,
            top_k=effective_top_k,
            project_scope=effective_scope,
        )
        result = await service.run_query(request)
        return json.dumps(
            {
                "ok": True,
                "sql": result.sql,
                "columns": result.columns,
                "rows": result.rows,
                "row_count": result.row_count,
                "retries": result.retries,
                "duration_ms": result.duration_ms,
                "formatted_text": result.formatted_text,
                "warning": result.warning,
            },
            ensure_ascii=False,
        )
    except Exception as exc:  # noqa: BLE001
        return json.dumps(
            {
                "ok": False,
                "error": f"{type(exc).__name__}: {exc}",
            },
            ensure_ascii=False,
        )
