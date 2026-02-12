"""Text-to-SQL policy settings wrapper."""

from __future__ import annotations

from dataclasses import dataclass

from app.config.settings import settings

DEFAULT_SQL_ALLOWLIST_TABLES: list[str] = [
    "tbl_ProjectInfo",
    "tbl_FormulaComposition",
    "tbl_RawMaterials",
    "tbl_InorganicFillers",
    "tbl_TestResults_Ink",
    "tbl_TestResults_Coating",
    "tbl_TestResults_3DPrint",
    "tbl_TestResults_Composite",
]


@dataclass(frozen=True)
class AgentSqlConfig:
    timeout_seconds: int
    max_retries: int
    allowlist_tables: list[str]


def get_agent_sql_config() -> AgentSqlConfig:
    allowlist_tables = list(settings.AGENT_SQL_ALLOWLIST_TABLES or [])
    if not allowlist_tables:
        allowlist_tables = list(DEFAULT_SQL_ALLOWLIST_TABLES)

    return AgentSqlConfig(
        timeout_seconds=settings.AGENT_SQL_TIMEOUT,
        max_retries=settings.AGENT_SQL_MAX_RETRIES,
        allowlist_tables=allowlist_tables,
    )
