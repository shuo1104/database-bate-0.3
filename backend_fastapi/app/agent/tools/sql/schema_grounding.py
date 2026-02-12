"""Schema grounding helpers for Text-to-SQL generation."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Iterable
from typing import Any

from app.config.settings import settings
from app.core.logger import logger

SampleProvider = Callable[[list[str]], Awaitable[dict[str, dict[str, Any]]]]

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

LOGICAL_TABLE_GROUPS: dict[str, list[str]] = {
    "projects": ["tbl_ProjectInfo"],
    "materials": ["tbl_RawMaterials"],
    "fillers": ["tbl_InorganicFillers"],
    "test_results": [
        "tbl_TestResults_Ink",
        "tbl_TestResults_Coating",
        "tbl_TestResults_3DPrint",
        "tbl_TestResults_Composite",
    ],
    "project_compositions": ["tbl_FormulaComposition"],
}

TABLE_COLUMN_HINTS: dict[str, list[dict[str, Any]]] = {
    "tbl_ProjectInfo": [
        {"name": "ProjectID", "type": "INTEGER", "nullable": False},
        {"name": "ProjectName", "type": "VARCHAR", "nullable": False},
        {"name": "ProjectType_FK", "type": "INTEGER", "nullable": True},
        {"name": "SubstrateApplication", "type": "TEXT", "nullable": True},
        {"name": "FormulaCode", "type": "VARCHAR", "nullable": True},
        {"name": "FormulatorName", "type": "VARCHAR", "nullable": True},
        {"name": "FormulationDate", "type": "DATE", "nullable": True},
    ],
    "tbl_FormulaComposition": [
        {"name": "CompositionID", "type": "INTEGER", "nullable": False},
        {"name": "ProjectID_FK", "type": "INTEGER", "nullable": False},
        {"name": "MaterialID_FK", "type": "INTEGER", "nullable": True},
        {"name": "FillerID_FK", "type": "INTEGER", "nullable": True},
        {"name": "WeightPercentage", "type": "NUMERIC", "nullable": False},
        {"name": "AdditionMethod", "type": "TEXT", "nullable": True},
        {"name": "Remarks", "type": "TEXT", "nullable": True},
    ],
    "tbl_RawMaterials": [
        {"name": "MaterialID", "type": "INTEGER", "nullable": False},
        {"name": "TradeName", "type": "VARCHAR", "nullable": False},
        {"name": "Category_FK", "type": "INTEGER", "nullable": True},
        {"name": "Supplier", "type": "VARCHAR", "nullable": True},
        {"name": "CAS_Number", "type": "VARCHAR", "nullable": True},
        {"name": "Density", "type": "NUMERIC", "nullable": True},
        {"name": "Viscosity", "type": "NUMERIC", "nullable": True},
        {"name": "FunctionDescription", "type": "TEXT", "nullable": True},
    ],
    "tbl_InorganicFillers": [
        {"name": "FillerID", "type": "INTEGER", "nullable": False},
        {"name": "TradeName", "type": "VARCHAR", "nullable": False},
        {"name": "FillerType_FK", "type": "INTEGER", "nullable": True},
        {"name": "Supplier", "type": "VARCHAR", "nullable": True},
        {"name": "ParticleSize", "type": "VARCHAR", "nullable": True},
        {"name": "IsSilanized", "type": "INTEGER", "nullable": True},
        {"name": "CouplingAgent", "type": "VARCHAR", "nullable": True},
        {"name": "SurfaceArea", "type": "NUMERIC", "nullable": True},
    ],
    "tbl_TestResults_Ink": [
        {"name": "ResultID", "type": "INTEGER", "nullable": False},
        {"name": "ProjectID_FK", "type": "INTEGER", "nullable": False},
        {"name": "Ink_Viscosity", "type": "VARCHAR", "nullable": True},
        {"name": "Ink_Reactivity", "type": "VARCHAR", "nullable": True},
        {"name": "Ink_ParticleSize", "type": "VARCHAR", "nullable": True},
        {"name": "Ink_SurfaceTension", "type": "VARCHAR", "nullable": True},
        {"name": "Ink_ColorValue", "type": "VARCHAR", "nullable": True},
        {"name": "Ink_RheologyNote", "type": "TEXT", "nullable": True},
        {"name": "TestDate", "type": "DATE", "nullable": True},
        {"name": "Notes", "type": "TEXT", "nullable": True},
    ],
    "tbl_TestResults_Coating": [
        {"name": "ResultID", "type": "INTEGER", "nullable": False},
        {"name": "ProjectID_FK", "type": "INTEGER", "nullable": False},
        {"name": "Coating_Adhesion", "type": "VARCHAR", "nullable": True},
        {"name": "Coating_Transparency", "type": "VARCHAR", "nullable": True},
        {"name": "Coating_SurfaceHardness", "type": "VARCHAR", "nullable": True},
        {"name": "Coating_ChemicalResistance", "type": "VARCHAR", "nullable": True},
        {"name": "Coating_CostEstimate", "type": "VARCHAR", "nullable": True},
        {"name": "TestDate", "type": "DATE", "nullable": True},
        {"name": "Notes", "type": "TEXT", "nullable": True},
    ],
    "tbl_TestResults_3DPrint": [
        {"name": "ResultID", "type": "INTEGER", "nullable": False},
        {"name": "ProjectID_FK", "type": "INTEGER", "nullable": False},
        {"name": "Print3D_Shrinkage", "type": "VARCHAR", "nullable": True},
        {"name": "Print3D_YoungsModulus", "type": "VARCHAR", "nullable": True},
        {"name": "Print3D_FlexuralStrength", "type": "VARCHAR", "nullable": True},
        {"name": "Print3D_ShoreHardness", "type": "VARCHAR", "nullable": True},
        {"name": "Print3D_ImpactResistance", "type": "VARCHAR", "nullable": True},
        {"name": "TestDate", "type": "DATE", "nullable": True},
        {"name": "Notes", "type": "TEXT", "nullable": True},
    ],
    "tbl_TestResults_Composite": [
        {"name": "ResultID", "type": "INTEGER", "nullable": False},
        {"name": "ProjectID_FK", "type": "INTEGER", "nullable": False},
        {"name": "Composite_FlexuralStrength", "type": "VARCHAR", "nullable": True},
        {"name": "Composite_YoungsModulus", "type": "VARCHAR", "nullable": True},
        {"name": "Composite_ImpactResistance", "type": "VARCHAR", "nullable": True},
        {"name": "Composite_ConversionRate", "type": "VARCHAR", "nullable": True},
        {"name": "Composite_WaterAbsorption", "type": "VARCHAR", "nullable": True},
        {"name": "TestDate", "type": "DATE", "nullable": True},
        {"name": "Notes", "type": "TEXT", "nullable": True},
    ],
}

RELATIONSHIP_HINTS: list[str] = [
    "tbl_FormulaComposition.ProjectID_FK -> tbl_ProjectInfo.ProjectID",
    "tbl_FormulaComposition.MaterialID_FK -> tbl_RawMaterials.MaterialID",
    "tbl_FormulaComposition.FillerID_FK -> tbl_InorganicFillers.FillerID",
    "tbl_TestResults_Ink.ProjectID_FK -> tbl_ProjectInfo.ProjectID",
    "tbl_TestResults_Coating.ProjectID_FK -> tbl_ProjectInfo.ProjectID",
    "tbl_TestResults_3DPrint.ProjectID_FK -> tbl_ProjectInfo.ProjectID",
    "tbl_TestResults_Composite.ProjectID_FK -> tbl_ProjectInfo.ProjectID",
]


def get_effective_allowlist_tables() -> list[str]:
    configured_tables = [
        str(table_name).strip()
        for table_name in (settings.AGENT_SQL_ALLOWLIST_TABLES or [])
        if str(table_name).strip()
    ]
    if configured_tables:
        return configured_tables
    return list(DEFAULT_SQL_ALLOWLIST_TABLES)


def _safe_sample_value(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if len(text) > 60:
        return f"{text[:57]}..."
    return text


def _resolve_logical_group(physical_table_name: str) -> str:
    for logical_name, physical_tables in LOGICAL_TABLE_GROUPS.items():
        if physical_table_name in physical_tables:
            return logical_name
    return "unknown"


async def build_schema_grounding_snapshot(
    *,
    sample_provider: SampleProvider | None = None,
    table_names: Iterable[str] | None = None,
) -> dict[str, Any]:
    selected_tables = (
        [str(item).strip() for item in table_names if str(item).strip()]
        if table_names is not None
        else get_effective_allowlist_tables()
    )

    sample_rows: dict[str, dict[str, Any]] = {}
    if sample_provider is not None and selected_tables:
        try:
            sample_rows = await sample_provider(selected_tables)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Failed to load schema grounding sample rows: %s: %s",
                type(exc).__name__,
                exc,
            )

    tables_payload: list[dict[str, Any]] = []
    available_tables: set[str] = set()

    for table_name in selected_tables:
        column_hints = TABLE_COLUMN_HINTS.get(table_name)
        if not column_hints:
            logger.warning("Schema grounding table hints not found: %s", table_name)
            continue

        available_tables.add(table_name)
        row_sample = sample_rows.get(table_name) or {}

        columns_payload: list[dict[str, Any]] = []
        for column in column_hints:
            sample_value = _safe_sample_value(row_sample.get(column["name"]))
            columns_payload.append(
                {
                    "name": column["name"],
                    "type": column["type"],
                    "nullable": bool(column["nullable"]),
                    "sample": sample_value,
                }
            )

        tables_payload.append(
            {
                "logical_name": _resolve_logical_group(table_name),
                "physical_name": table_name,
                "columns": columns_payload,
            }
        )

    relationships_payload = [
        hint
        for hint in RELATIONSHIP_HINTS
        if hint.split(" -> ")[0].split(".")[0] in available_tables
        and hint.split(" -> ")[1].split(".")[0] in available_tables
    ]

    return {
        "tables": tables_payload,
        "relationships": relationships_payload,
        "logical_groups": LOGICAL_TABLE_GROUPS,
    }


def render_schema_grounding(snapshot: dict[str, Any]) -> str:
    table_lines: list[str] = []
    for table in snapshot.get("tables", []):
        table_lines.append(f"- [{table['logical_name']}] {table['physical_name']}")
        for column in table.get("columns", []):
            sample_suffix = (
                f", sample={column['sample']}" if column.get("sample") else ""
            )
            nullable_suffix = "nullable" if column.get("nullable") else "not-null"
            table_lines.append(
                f"  - {column['name']} ({column['type']}, {nullable_suffix}{sample_suffix})"
            )

    relation_lines = [f"- {item}" for item in snapshot.get("relationships", [])]

    if not table_lines:
        table_lines = ["- (no table metadata available)"]
    if not relation_lines:
        relation_lines = ["- (no relationship metadata available)"]

    return (
        "Tables:\n"
        + "\n".join(table_lines)
        + "\n\nRelationships:\n"
        + "\n".join(relation_lines)
    )
