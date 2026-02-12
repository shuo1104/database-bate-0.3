"""LangChain tool wrapper for Phase 1 document ingest."""

from __future__ import annotations

import json
from pathlib import Path

from langchain_core.tools import tool


@tool("agent_document_ingest")
def agent_document_ingest(file_path: str, file_type: str = "") -> str:
    """Prepare ingest intent for a local document path.

    Use this tool when a user gives a local file path and asks the agent to ingest it.
    The API layer executes the real async ingest workflow and returns task_id.
    """

    normalized_path = str(Path(file_path))
    normalized_type = file_type.strip().lower() if file_type else Path(file_path).suffix

    payload = {
        "accepted": True,
        "file_path": normalized_path,
        "file_type": normalized_type,
        "next_action": "Call POST /api/v1/agent/ingest with multipart file to create task_id",
    }
    return json.dumps(payload, ensure_ascii=False)
