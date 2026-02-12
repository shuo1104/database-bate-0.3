"""Phase 2 unit tests for schema grounding helpers."""

from __future__ import annotations

import unittest
from typing import Any

from app.agent.tools.sql.schema_grounding import (
    DEFAULT_SQL_ALLOWLIST_TABLES,
    TABLE_COLUMN_HINTS,
    build_schema_grounding_snapshot,
    get_effective_allowlist_tables,
    render_schema_grounding,
)


class SchemaGroundingTableHintsTests(unittest.TestCase):
    """Verify TABLE_COLUMN_HINTS covers all allowlist tables."""

    def test_all_allowlist_tables_have_hints(self) -> None:
        for table_name in DEFAULT_SQL_ALLOWLIST_TABLES:
            self.assertIn(
                table_name,
                TABLE_COLUMN_HINTS,
                f"TABLE_COLUMN_HINTS missing entry for allowlist table: {table_name}",
            )

    def test_each_table_has_at_least_two_columns(self) -> None:
        for table_name, columns in TABLE_COLUMN_HINTS.items():
            self.assertGreaterEqual(
                len(columns),
                2,
                f"Table {table_name} should have at least 2 column hints",
            )

    def test_column_hint_keys(self) -> None:
        required_keys = {"name", "type", "nullable"}
        for table_name, columns in TABLE_COLUMN_HINTS.items():
            for column in columns:
                self.assertTrue(
                    required_keys.issubset(column.keys()),
                    f"Column hint in {table_name} missing required keys: {column}",
                )


class GetEffectiveAllowlistTablesTests(unittest.TestCase):
    def test_returns_default_when_settings_empty(self) -> None:
        tables = get_effective_allowlist_tables()
        self.assertIsInstance(tables, list)
        self.assertGreater(len(tables), 0)


class BuildSchemaGroundingSnapshotTests(unittest.IsolatedAsyncioTestCase):
    async def test_snapshot_without_sample_provider(self) -> None:
        snapshot = await build_schema_grounding_snapshot()
        self.assertIn("tables", snapshot)
        self.assertIn("relationships", snapshot)
        self.assertGreater(len(snapshot["tables"]), 0)

    async def test_snapshot_with_mock_sample_provider(self) -> None:
        async def mock_provider(
            table_names: list[str],
        ) -> dict[str, dict[str, Any]]:
            return {
                "tbl_ProjectInfo": {
                    "ProjectID": 1,
                    "ProjectName": "Demo",
                }
            }

        snapshot = await build_schema_grounding_snapshot(
            sample_provider=mock_provider,
            table_names=["tbl_ProjectInfo"],
        )
        tables = snapshot["tables"]
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0]["physical_name"], "tbl_ProjectInfo")

        # Verify sample values are included
        columns = tables[0]["columns"]
        project_id_col = next(c for c in columns if c["name"] == "ProjectID")
        self.assertEqual(project_id_col["sample"], "1")

    async def test_snapshot_filters_by_table_names(self) -> None:
        snapshot = await build_schema_grounding_snapshot(
            table_names=["tbl_ProjectInfo", "tbl_RawMaterials"],
        )
        physical_names = [t["physical_name"] for t in snapshot["tables"]]
        self.assertEqual(physical_names, ["tbl_ProjectInfo", "tbl_RawMaterials"])

    async def test_snapshot_skips_unknown_table(self) -> None:
        snapshot = await build_schema_grounding_snapshot(
            table_names=["tbl_NonExistent"],
        )
        self.assertEqual(len(snapshot["tables"]), 0)


class RenderSchemaGroundingTests(unittest.TestCase):
    def test_render_non_empty_snapshot(self) -> None:
        snapshot = {
            "tables": [
                {
                    "logical_name": "projects",
                    "physical_name": "tbl_ProjectInfo",
                    "columns": [
                        {
                            "name": "ProjectID",
                            "type": "INTEGER",
                            "nullable": False,
                            "sample": "1",
                        },
                    ],
                }
            ],
            "relationships": [
                "tbl_FormulaComposition.ProjectID_FK -> tbl_ProjectInfo.ProjectID"
            ],
        }
        text = render_schema_grounding(snapshot)
        self.assertIn("Tables:", text)
        self.assertIn("tbl_ProjectInfo", text)
        self.assertIn("ProjectID", text)
        self.assertIn("sample=1", text)
        self.assertIn("Relationships:", text)

    def test_render_empty_snapshot(self) -> None:
        snapshot = {"tables": [], "relationships": []}
        text = render_schema_grounding(snapshot)
        self.assertIn("no table metadata available", text)
        self.assertIn("no relationship metadata available", text)


if __name__ == "__main__":
    unittest.main()
