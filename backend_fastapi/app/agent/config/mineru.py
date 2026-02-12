"""MinerU API settings wrapper."""

from __future__ import annotations

from dataclasses import dataclass

from app.config.settings import settings


@dataclass(frozen=True)
class MinerUConfig:
    api_url: str
    api_key: str
    parse_path: str
    timeout_seconds: int


def get_mineru_config() -> MinerUConfig:
    return MinerUConfig(
        api_url=settings.MINERU_API_URL,
        api_key=settings.MINERU_API_KEY,
        parse_path=settings.MINERU_PARSE_PATH,
        timeout_seconds=settings.MINERU_API_TIMEOUT,
    )
