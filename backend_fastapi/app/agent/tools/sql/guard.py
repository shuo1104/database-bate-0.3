"""SQL safety guard for Text-to-SQL queries."""

from __future__ import annotations

import re

from app.core.custom_exceptions import ValidationException


class SqlSafetyGuard:
    """Validate generated SQL against safety constraints."""

    _DISALLOWED_KEYWORDS = re.compile(
        r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|MERGE|GRANT|REVOKE|COPY|VACUUM|ANALYZE)\b",
        flags=re.IGNORECASE,
    )
    _TABLE_PATTERN = re.compile(
        r"\b(?:FROM|JOIN)\s+([\w\.\"]+)",
        flags=re.IGNORECASE,
    )
    _UNION_PATTERN = re.compile(r"\bUNION(?:\s+ALL)?\b", flags=re.IGNORECASE)

    def __init__(
        self,
        *,
        allowlist_tables: list[str],
        max_subquery_depth: int = 2,
        max_union_count: int = 3,
        require_where: bool = True,
    ) -> None:
        self._allowlist_tables = {table.lower() for table in allowlist_tables}
        self._max_subquery_depth = max_subquery_depth
        self._max_union_count = max_union_count
        self._require_where = require_where

    def validate(self, sql: str) -> str:
        sanitized_sql = self._normalize_sql(sql)
        normalized_upper = sanitized_sql.upper()

        self._ensure_single_statement(sanitized_sql)
        self._ensure_readonly_statement(normalized_upper)
        self._ensure_disallowed_keywords_absent(normalized_upper)
        self._ensure_allowlist_tables(sanitized_sql)
        self._ensure_union_limit(normalized_upper)
        self._ensure_subquery_depth(normalized_upper)
        self._ensure_where_clause(normalized_upper)

        return sanitized_sql

    @staticmethod
    def _normalize_sql(sql: str) -> str:
        compact_sql = (sql or "").strip()
        if not compact_sql:
            raise ValidationException("Generated SQL is empty")

        compact_sql = re.sub(r"--.*?$", "", compact_sql, flags=re.MULTILINE)
        compact_sql = re.sub(r"/\*.*?\*/", "", compact_sql, flags=re.DOTALL)
        compact_sql = compact_sql.strip()
        if compact_sql.endswith(";"):
            compact_sql = compact_sql[:-1].strip()

        if not compact_sql:
            raise ValidationException("Generated SQL is empty after normalization")

        return compact_sql

    @staticmethod
    def _ensure_single_statement(sql: str) -> None:
        if ";" in sql:
            raise ValidationException("Multiple SQL statements are not allowed")

    @staticmethod
    def _ensure_readonly_statement(normalized_upper: str) -> None:
        starts_with_select = normalized_upper.startswith("SELECT ")
        starts_with_with = normalized_upper.startswith("WITH ")
        if not starts_with_select and not starts_with_with:
            raise ValidationException("Only SELECT queries are allowed")

    def _ensure_disallowed_keywords_absent(self, normalized_upper: str) -> None:
        match = self._DISALLOWED_KEYWORDS.search(normalized_upper)
        if match:
            raise ValidationException(
                f"Disallowed SQL keyword detected: {match.group(1).upper()}"
            )

    def _ensure_allowlist_tables(self, sql: str) -> None:
        referenced_tables = self._extract_tables(sql)
        if not referenced_tables:
            raise ValidationException("No table reference found in SQL query")

        blocked_tables = [
            table
            for table in referenced_tables
            if table.lower() not in self._allowlist_tables
        ]
        if blocked_tables:
            blocked_text = ", ".join(sorted(set(blocked_tables)))
            raise ValidationException(
                f"Referenced table is not in allowlist: {blocked_text}"
            )

    def _ensure_union_limit(self, normalized_upper: str) -> None:
        union_count = len(self._UNION_PATTERN.findall(normalized_upper))
        if union_count > self._max_union_count:
            raise ValidationException(
                f"UNION count exceeded: {union_count} > {self._max_union_count}"
            )

    def _ensure_subquery_depth(self, normalized_upper: str) -> None:
        max_select_depth = self._max_select_parenthesis_depth(normalized_upper)
        if max_select_depth > self._max_subquery_depth:
            raise ValidationException(
                "Subquery nesting exceeded: "
                f"{max_select_depth} > {self._max_subquery_depth}"
            )

    def _ensure_where_clause(self, normalized_upper: str) -> None:
        if self._require_where and " WHERE " not in f" {normalized_upper} ":
            raise ValidationException(
                "Query must include a WHERE clause to avoid full scans"
            )

    @classmethod
    def _extract_tables(cls, sql: str) -> list[str]:
        matched_tables: list[str] = []
        for match in cls._TABLE_PATTERN.finditer(sql):
            raw_name = match.group(1).strip()
            if raw_name.startswith("("):
                continue
            normalized_name = cls._normalize_table_name(raw_name)
            if normalized_name:
                matched_tables.append(normalized_name)
        return matched_tables

    @staticmethod
    def _normalize_table_name(raw_name: str) -> str:
        table_name = raw_name.strip().strip('"')
        if "." in table_name:
            table_name = table_name.split(".")[-1]
        return table_name.strip('"')

    @staticmethod
    def _max_select_parenthesis_depth(normalized_upper: str) -> int:
        depth = 0
        max_select_depth = 0
        idx = 0
        total_length = len(normalized_upper)

        while idx < total_length:
            char = normalized_upper[idx]

            if char == "(":
                depth += 1
                idx += 1
                continue
            if char == ")":
                depth = max(depth - 1, 0)
                idx += 1
                continue

            if normalized_upper.startswith("SELECT", idx):
                prev_char = normalized_upper[idx - 1] if idx > 0 else " "
                next_idx = idx + 6
                next_char = (
                    normalized_upper[next_idx] if next_idx < total_length else " "
                )
                if not (prev_char.isalnum() or prev_char == "_") and not (
                    next_char.isalnum() or next_char == "_"
                ):
                    max_select_depth = max(max_select_depth, depth)
                    idx += 6
                    continue

            idx += 1

        return max_select_depth
