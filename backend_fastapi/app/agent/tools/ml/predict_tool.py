"""LangChain tool placeholder for ML inference."""

from __future__ import annotations

import json
from typing import Any

from langchain_core.tools import tool

from app.agent.schemas import MLPredictionInputSchema


def _parse_features(features_json: str) -> list[dict[str, Any]]:
    raw_value = (features_json or "").strip()
    if not raw_value:
        return []

    decoded = json.loads(raw_value)
    if isinstance(decoded, list):
        normalized: list[dict[str, Any]] = []
        for index, item in enumerate(decoded):
            if isinstance(item, dict):
                normalized.append(item)
            else:
                normalized.append({"name": f"feature_{index}", "value": item})
        return normalized

    if isinstance(decoded, dict):
        return [{"name": str(key), "value": value} for key, value in decoded.items()]

    raise ValueError("features_json must decode to list or object")


def _parse_context(context_json: str) -> dict[str, Any]:
    raw_value = (context_json or "").strip()
    if not raw_value:
        return {}

    decoded = json.loads(raw_value)
    if not isinstance(decoded, dict):
        raise ValueError("context_json must decode to object")
    return decoded


@tool("agent_ml_predict_placeholder")
def agent_ml_predict_placeholder(
    model_name: str = "default",
    features_json: str = "[]",
    context_json: str = "{}",
) -> str:
    """Phase 3 placeholder tool for future ML inference integration."""

    try:
        request = MLPredictionInputSchema(
            model_name=model_name,
            features=_parse_features(features_json),
            context=_parse_context(context_json),
        )
    except Exception as exc:  # noqa: BLE001
        return json.dumps(
            {
                "ok": False,
                "status": "invalid_request",
                "error": f"{type(exc).__name__}: {exc}",
            },
            ensure_ascii=False,
        )

    return json.dumps(
        {
            "ok": False,
            "status": "not_implemented",
            "message": (
                "ML inference is not implemented yet. "
                "Wire model service in Phase 3+ before enabling this tool in production."
            ),
            "request_preview": request.model_dump(),
        },
        ensure_ascii=False,
    )
