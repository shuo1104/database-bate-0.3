"""Deepseek client and connectivity checks."""

from __future__ import annotations

from typing import Any

from openai import OpenAI

from app.agent.config import get_deepseek_config


def create_deepseek_client() -> OpenAI:
    cfg = get_deepseek_config()
    return OpenAI(api_key=cfg.api_key, base_url=cfg.base_url)


def check_deepseek_connectivity(timeout_seconds: float = 15.0) -> dict[str, Any]:
    """Validate Deepseek API connectivity through OpenAI-compatible SDK.

    Returns a machine-friendly result:
    - status=ok: API reachable
    - status=skipped: missing API key
    - status=error: request failed
    """

    cfg = get_deepseek_config()
    if not cfg.api_key:
        return {
            "status": "skipped",
            "reason": "DEEPSEEK_API_KEY is empty",
            "base_url": cfg.base_url,
            "model": cfg.model,
        }

    client = create_deepseek_client()
    try:
        response = client.chat.completions.create(
            model=cfg.model,
            messages=[
                {"role": "system", "content": "You are a health-check assistant."},
                {"role": "user", "content": "Reply with: ok"},
            ],
            temperature=0,
            max_tokens=8,
            timeout=timeout_seconds,
        )
        text = (response.choices[0].message.content or "").strip()
        return {
            "status": "ok",
            "reply": text,
            "base_url": cfg.base_url,
            "model": cfg.model,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "error",
            "reason": f"{type(exc).__name__}: {exc}",
            "base_url": cfg.base_url,
            "model": cfg.model,
        }
