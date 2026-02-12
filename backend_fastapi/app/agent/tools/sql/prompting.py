"""Prompt builders for Text-to-SQL generation and repair."""

from __future__ import annotations

from typing import Any


def build_sql_generation_prompts(
    *,
    question: str,
    schema_grounding_text: str,
    top_k: int,
    project_scope: list[int] | None = None,
    previous_sql: str | None = None,
    previous_error: str | None = None,
) -> tuple[str, str]:
    system_prompt = (
        "You are a strict PostgreSQL Text-to-SQL generator. "
        "Return SQL only. Never add markdown, explanation, or comments. "
        "Always output a single SELECT query."
    )

    retry_block = ""
    if previous_error:
        retry_block = (
            "\n\nPrevious attempt failed. Repair the query."
            f"\nPrevious SQL:\n{previous_sql or '(none)'}"
            f"\nDatabase/Error feedback:\n{previous_error}"
        )

    scope_block = ""
    if project_scope:
        safe_ids = sorted({int(item) for item in project_scope})
        scope_ids_text = ", ".join(str(item) for item in safe_ids)
        scope_block = (
            "\n7) Enforce row-level scope by restricting project identifier "
            f"to ProjectID / ProjectID_FK in ({scope_ids_text})."
        )
    scope_suffix = "\n" if scope_block else ""

    user_prompt = (
        "Generate one PostgreSQL SELECT statement for this user question.\n"
        f"Question: {question}\n\n"
        "Hard constraints:\n"
        "1) SELECT-only query. Never generate INSERT/UPDATE/DELETE/DDL.\n"
        "2) Use only tables listed in schema grounding.\n"
        "3) Include a WHERE clause to avoid full table scans.\n"
        f"4) Include LIMIT <= {top_k}.\n"
        "5) Keep UNION count <= 3 and subquery nesting depth <= 2.\n"
        "6) Keep column/table names exact.\n\n"
        f"{scope_block}"
        f"{scope_suffix}"
        f"Schema grounding:\n{schema_grounding_text}"
        f"{retry_block}"
    )

    return system_prompt, user_prompt


def extract_sql_from_llm_output(content: Any) -> str:
    text = str(content or "").strip()
    if not text:
        return ""

    if text.startswith("```"):
        text = text.strip("`").strip()
        if text.lower().startswith("sql"):
            text = text[3:].strip()

    upper_text = text.upper()
    select_index = upper_text.find("SELECT")
    with_index = upper_text.find("WITH")

    if select_index == -1 and with_index == -1:
        return text

    if with_index != -1 and (select_index == -1 or with_index < select_index):
        return text[with_index:].strip().rstrip(";")
    return text[select_index:].strip().rstrip(";")
