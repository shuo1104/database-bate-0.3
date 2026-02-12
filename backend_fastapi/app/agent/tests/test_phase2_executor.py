"""Phase 2 unit tests for SQL executor static/class methods."""

from __future__ import annotations

import unittest
from datetime import date, datetime
from decimal import Decimal

from app.agent.tools.sql.executor import SqlReadonlyExecutor


class WrapWithLimitTests(unittest.TestCase):
    """Test SqlReadonlyExecutor._wrap_with_limit (static, no DB needed)."""

    def test_basic_wrapping(self) -> None:
        sql = 'SELECT "ProjectID" FROM "tbl_ProjectInfo" WHERE "ProjectID" = 1'
        result = SqlReadonlyExecutor._wrap_with_limit(sql, 100)
        self.assertIn("LIMIT 100", result)
        self.assertIn("agent_sql_result", result)

    def test_strips_trailing_semicolon(self) -> None:
        sql = "SELECT 1 WHERE 1=1;"
        result = SqlReadonlyExecutor._wrap_with_limit(sql, 10)
        # The inner SQL should not have semicolon
        self.assertNotIn(";;", result)
        self.assertIn("LIMIT 10", result)

    def test_clamps_top_k_to_minimum_one(self) -> None:
        result = SqlReadonlyExecutor._wrap_with_limit("SELECT 1 WHERE 1=1", 0)
        self.assertIn("LIMIT 1", result)

    def test_clamps_top_k_to_maximum_1000(self) -> None:
        result = SqlReadonlyExecutor._wrap_with_limit("SELECT 1 WHERE 1=1", 9999)
        self.assertIn("LIMIT 1000", result)

    def test_handles_empty_sql(self) -> None:
        result = SqlReadonlyExecutor._wrap_with_limit("", 10)
        self.assertIn("LIMIT 10", result)


class SerializeValueTests(unittest.TestCase):
    """Test SqlReadonlyExecutor._serialize_value (static, no DB needed)."""

    def test_decimal_to_float(self) -> None:
        result = SqlReadonlyExecutor._serialize_value(Decimal("3.14"))
        self.assertIsInstance(result, float)
        self.assertAlmostEqual(result, 3.14)

    def test_datetime_to_iso(self) -> None:
        dt = datetime(2025, 6, 15, 10, 30, 0)
        result = SqlReadonlyExecutor._serialize_value(dt)
        self.assertEqual(result, "2025-06-15T10:30:00")

    def test_date_to_iso(self) -> None:
        d = date(2025, 6, 15)
        result = SqlReadonlyExecutor._serialize_value(d)
        self.assertEqual(result, "2025-06-15")

    def test_string_passthrough(self) -> None:
        self.assertEqual(SqlReadonlyExecutor._serialize_value("hello"), "hello")

    def test_int_passthrough(self) -> None:
        self.assertEqual(SqlReadonlyExecutor._serialize_value(42), 42)

    def test_none_passthrough(self) -> None:
        self.assertIsNone(SqlReadonlyExecutor._serialize_value(None))


class IsSafeTableNameTests(unittest.TestCase):
    """Test SqlReadonlyExecutor._is_safe_table_name (static, no DB needed)."""

    def test_valid_table_names(self) -> None:
        self.assertTrue(SqlReadonlyExecutor._is_safe_table_name("tbl_ProjectInfo"))
        self.assertTrue(SqlReadonlyExecutor._is_safe_table_name("tbl_TestResults_Ink"))

    def test_rejects_special_characters(self) -> None:
        self.assertFalse(SqlReadonlyExecutor._is_safe_table_name("tbl; DROP TABLE"))
        self.assertFalse(SqlReadonlyExecutor._is_safe_table_name("table--name"))

    def test_empty_string(self) -> None:
        self.assertFalse(SqlReadonlyExecutor._is_safe_table_name(""))


class ProjectScopeFilterTests(unittest.TestCase):
    def test_no_scope_keeps_sql(self) -> None:
        sql = "SELECT * FROM (SELECT 1) AS agent_sql_result LIMIT 10"
        result = SqlReadonlyExecutor._apply_project_scope_filter(sql, None)
        self.assertEqual(result, sql)

    def test_scope_injects_filter(self) -> None:
        sql = "SELECT * FROM (SELECT 1) AS agent_sql_result LIMIT 10"
        result = SqlReadonlyExecutor._apply_project_scope_filter(sql, [3, 1, 3])
        self.assertIn("agent_scope_result", result)
        self.assertIn("ProjectID", result)
        self.assertIn("ProjectID_FK", result)
        self.assertIn("IN (1, 3)", result)


class SerializeRowTests(unittest.TestCase):
    """Test SqlReadonlyExecutor._serialize_row (classmethod, no DB needed)."""

    def test_mixed_types(self) -> None:
        row = {
            "id": 1,
            "price": Decimal("9.99"),
            "created": datetime(2025, 1, 1, 12, 0, 0),
            "name": "Test",
            "empty": None,
        }
        result = SqlReadonlyExecutor._serialize_row(row)
        self.assertEqual(result["id"], 1)
        self.assertAlmostEqual(result["price"], 9.99)
        self.assertEqual(result["created"], "2025-01-01T12:00:00")
        self.assertEqual(result["name"], "Test")
        self.assertIsNone(result["empty"])


if __name__ == "__main__":
    unittest.main()
