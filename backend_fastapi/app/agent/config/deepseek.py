"""Deepseek settings wrapper.

Deepseek provides an OpenAI-compatible API. We keep all tunables in
app.config.settings.settings and expose a small typed facade here.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.config.settings import settings


@dataclass(frozen=True)
class DeepseekConfig:
    api_key: str
    base_url: str
    model: str
    temperature: float
    max_tokens: int


def get_deepseek_config() -> DeepseekConfig:
    return DeepseekConfig(
        api_key=settings.DEEPSEEK_API_KEY,
        base_url=settings.DEEPSEEK_BASE_URL,
        model=settings.DEEPSEEK_MODEL,
        temperature=settings.AGENT_LLM_TEMPERATURE,
        max_tokens=settings.AGENT_LLM_MAX_TOKENS,
    )
