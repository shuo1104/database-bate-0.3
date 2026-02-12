"""LangChain callback handler for audit trace collection."""

from __future__ import annotations

from time import perf_counter
from typing import Any

from langchain_core.callbacks.base import BaseCallbackHandler


class AgentAuditCallbackHandler(BaseCallbackHandler):
    """Collect tool-level traces for audit persistence."""

    raise_error = False

    def __init__(self) -> None:
        self._start_ts: dict[str, float] = {}
        self.events: list[dict[str, Any]] = []

    def on_tool_start(
        self,
        serialized: dict[str, Any],
        input_str: str,
        *,
        run_id: Any,
        parent_run_id: Any | None = None,
        **kwargs: Any,
    ) -> Any:
        _ = parent_run_id, kwargs
        tool_name = (
            serialized.get("name")
            or serialized.get("id")
            or serialized.get("lc")
            or "unknown_tool"
        )
        run_key = str(run_id)
        self._start_ts[run_key] = perf_counter()
        self.events.append(
            {
                "run_id": run_key,
                "tool_name": str(tool_name),
                "status": "started",
                "tool_input": self._truncate(input_str),
            }
        )
        return None

    def on_tool_end(
        self,
        output: Any,
        *,
        run_id: Any,
        parent_run_id: Any | None = None,
        **kwargs: Any,
    ) -> Any:
        _ = parent_run_id, kwargs
        run_key = str(run_id)
        duration_ms = self._consume_duration_ms(run_key)

        self.events.append(
            {
                "run_id": run_key,
                "status": "ok",
                "tool_output": self._truncate(output),
                "duration_ms": duration_ms,
            }
        )
        return None

    def on_tool_error(
        self,
        error: BaseException,
        *,
        run_id: Any,
        parent_run_id: Any | None = None,
        **kwargs: Any,
    ) -> Any:
        _ = parent_run_id, kwargs
        run_key = str(run_id)
        duration_ms = self._consume_duration_ms(run_key)

        self.events.append(
            {
                "run_id": run_key,
                "status": "failed",
                "error": f"{type(error).__name__}: {error}",
                "duration_ms": duration_ms,
            }
        )
        return None

    @staticmethod
    def _truncate(value: Any, limit: int = 1000) -> str:
        text = str(value)
        if len(text) <= limit:
            return text
        return f"{text[:limit]}..."

    def _consume_duration_ms(self, run_key: str) -> int | None:
        start = self._start_ts.pop(run_key, None)
        if start is None:
            return None
        return int((perf_counter() - start) * 1000)
