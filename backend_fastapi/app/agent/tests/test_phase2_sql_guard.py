"""Phase 2 unit tests for SQL safety guard."""

from __future__ import annotations

import unittest

from app.agent.tools.sql.guard import SqlSafetyGuard
from app.core.custom_exceptions import ValidationException


class Phase2SqlGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.guard = SqlSafetyGuard(
            allowlist_tables=[
                "tbl_ProjectInfo",
                "tbl_FormulaComposition",
                "tbl_RawMaterials",
            ],
            max_subquery_depth=2,
            max_union_count=3,
            require_where=True,
        )

    def test_valid_select_sql_passes(self) -> None:
        sql = (
            'SELECT p."ProjectID", p."ProjectName" '
            'FROM "tbl_ProjectInfo" p '
            'WHERE p."ProjectID" = 1'
        )
        result = self.guard.validate(sql)
        self.assertIn("SELECT", result.upper())

    def test_rejects_dml(self) -> None:
        with self.assertRaises(ValidationException):
            self.guard.validate('UPDATE "tbl_ProjectInfo" SET "ProjectName" = \'x\'')

    def test_rejects_disallowed_table(self) -> None:
        with self.assertRaises(ValidationException):
            self.guard.validate('SELECT * FROM "tbl_Users" WHERE "UserID" = 1')

    def test_rejects_query_without_where(self) -> None:
        with self.assertRaises(ValidationException):
            self.guard.validate('SELECT * FROM "tbl_ProjectInfo"')

    def test_rejects_union_over_limit(self) -> None:
        sql = (
            'SELECT "ProjectID" FROM "tbl_ProjectInfo" WHERE "ProjectID" = 1 '
            'UNION SELECT "ProjectID" FROM "tbl_ProjectInfo" WHERE "ProjectID" = 2 '
            'UNION SELECT "ProjectID" FROM "tbl_ProjectInfo" WHERE "ProjectID" = 3 '
            'UNION SELECT "ProjectID" FROM "tbl_ProjectInfo" WHERE "ProjectID" = 4 '
            'UNION SELECT "ProjectID" FROM "tbl_ProjectInfo" WHERE "ProjectID" = 5'
        )
        with self.assertRaises(ValidationException):
            self.guard.validate(sql)

    def test_rejects_subquery_depth_over_limit(self) -> None:
        sql = (
            'SELECT * FROM "tbl_ProjectInfo" '
            'WHERE "ProjectID" IN ('
            'SELECT "ProjectID_FK" FROM "tbl_FormulaComposition" '
            'WHERE "MaterialID_FK" IN ('
            'SELECT "MaterialID" FROM "tbl_RawMaterials" '
            'WHERE "MaterialID" IN ('
            'SELECT "MaterialID" FROM "tbl_RawMaterials" WHERE "MaterialID" = 1'
            ")"
            ")"
            ")"
        )
        with self.assertRaises(ValidationException):
            self.guard.validate(sql)


if __name__ == "__main__":
    unittest.main()
