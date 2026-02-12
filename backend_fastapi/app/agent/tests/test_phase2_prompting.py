"""Phase 2 unit tests for SQL prompt building and LLM output extraction."""

from __future__ import annotations

import unittest

from app.agent.tools.sql.prompting import (
    build_sql_generation_prompts,
    extract_sql_from_llm_output,
)


class BuildSqlGenerationPromptsTests(unittest.TestCase):
    def test_basic_prompt_structure(self) -> None:
        system, user = build_sql_generation_prompts(
            question="query project information",
            schema_grounding_text="Tables:\n- tbl_ProjectInfo",
            top_k=100,
        )
        self.assertIn("PostgreSQL", system)
        self.assertIn("SELECT", system)
        self.assertIn("query project information", user)
        self.assertIn("tbl_ProjectInfo", user)
        self.assertIn("100", user)

    def test_retry_prompt_includes_previous_error(self) -> None:
        system, user = build_sql_generation_prompts(
            question="query projects",
            schema_grounding_text="Tables:\n- tbl_ProjectInfo",
            top_k=10,
            previous_sql="SELECT * FROM bad_table",
            previous_error="ValidationException: table not in allowlist",
        )
        self.assertIn("Previous attempt failed", user)
        self.assertIn("SELECT * FROM bad_table", user)
        self.assertIn("ValidationException", user)

    def test_scope_prompt_includes_project_ids(self) -> None:
        _, user = build_sql_generation_prompts(
            question="query projects",
            schema_grounding_text="Tables:\n- tbl_ProjectInfo",
            top_k=10,
            project_scope=[1, 3],
        )
        self.assertIn("ProjectID / ProjectID_FK", user)
        self.assertIn("(1, 3)", user)

    def test_no_retry_block_when_no_error(self) -> None:
        _, user = build_sql_generation_prompts(
            question="test",
            schema_grounding_text="schema",
            top_k=10,
        )
        self.assertNotIn("Previous attempt failed", user)


class ExtractSqlFromLlmOutputTests(unittest.TestCase):
    def test_plain_select(self) -> None:
        result = extract_sql_from_llm_output(
            'SELECT "ProjectID" FROM "tbl_ProjectInfo" WHERE "ProjectID" = 1'
        )
        self.assertTrue(result.startswith("SELECT"))

    def test_markdown_code_block(self) -> None:
        raw = '```sql\nSELECT "ProjectID" FROM "tbl_ProjectInfo" WHERE "ProjectID" = 1;\n```'
        result = extract_sql_from_llm_output(raw)
        self.assertTrue(result.startswith("SELECT"))
        self.assertNotIn("```", result)
        self.assertFalse(result.endswith(";"))

    def test_markdown_without_sql_tag(self) -> None:
        raw = "```\nSELECT 1 WHERE 1=1\n```"
        result = extract_sql_from_llm_output(raw)
        self.assertTrue(result.startswith("SELECT"))

    def test_text_with_explanation_before_sql(self) -> None:
        raw = "Here is the query:\nSELECT * FROM tbl_ProjectInfo WHERE ProjectID = 1;"
        result = extract_sql_from_llm_output(raw)
        self.assertTrue(result.startswith("SELECT"))

    def test_with_cte(self) -> None:
        raw = "WITH cte AS (SELECT 1) SELECT * FROM cte WHERE 1=1"
        result = extract_sql_from_llm_output(raw)
        self.assertTrue(result.startswith("WITH"))

    def test_empty_input(self) -> None:
        self.assertEqual(extract_sql_from_llm_output(""), "")
        self.assertEqual(extract_sql_from_llm_output(None), "")

    def test_no_sql_keyword_returns_text(self) -> None:
        result = extract_sql_from_llm_output("I cannot generate that query")
        self.assertEqual(result, "I cannot generate that query")

    def test_trailing_semicolon_stripped(self) -> None:
        result = extract_sql_from_llm_output("SELECT 1 WHERE 1=1;")
        self.assertFalse(result.endswith(";"))


if __name__ == "__main__":
    unittest.main()
