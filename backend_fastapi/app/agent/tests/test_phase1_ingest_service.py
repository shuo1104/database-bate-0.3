"""Phase 1 ingest service tests with external calls mocked."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.agent.config import DeepseekConfig, MinerUConfig
from app.api.v1.modules.agent.schema import AgentReviewUpdateRequest
from app.api.v1.modules.agent.service import AgentIngestService
from app.core.custom_exceptions import ExternalServiceException, ValidationException


class _FakeResponse:
    def __init__(
        self,
        status_code: int,
        *,
        text: str = "",
        json_payload: dict | None = None,
    ) -> None:
        self.status_code = status_code
        self.text = text
        self._json_payload = json_payload or {}

    def json(self) -> dict:
        return self._json_payload


class Phase1IngestServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_parse_document_routes_csv_to_local_parser(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", encoding="utf-8", delete=False
        ) as file_obj:
            file_obj.write("name,value\nalpha,1\nbeta,2\n")
            csv_path = file_obj.name

        try:
            result = await AgentIngestService.parse_document_with_mineru(
                csv_path,
                "sample.csv",
            )
            self.assertEqual(result["source"], "csv_local")
            self.assertEqual(result["structured_content"]["row_count"], 2)
        finally:
            Path(csv_path).unlink(missing_ok=True)

    async def test_parse_document_calls_mineru_for_pdf(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as file_obj:
            file_obj.write(b"%PDF-1.4 mock")
            pdf_path = file_obj.name

        try:
            with patch.object(
                AgentIngestService,
                "_call_mineru_api",
                new=AsyncMock(
                    return_value={
                        "raw_text": "parsed by mineru",
                        "structured_content": {},
                        "source": "mineru",
                    }
                ),
            ) as mock_call:
                result = await AgentIngestService.parse_document_with_mineru(
                    pdf_path,
                    "sample.pdf",
                )

            mock_call.assert_awaited_once()
            self.assertEqual(result["source"], "mineru")
        finally:
            Path(pdf_path).unlink(missing_ok=True)

    async def test_extract_structured_data_fallback_when_no_api_key(self) -> None:
        cfg = DeepseekConfig(
            api_key="",
            base_url="https://api.deepseek.com/v1",
            model="deepseek-chat",
            temperature=0.2,
            max_tokens=256,
        )

        with patch(
            "app.api.v1.modules.agent.service.get_deepseek_config", return_value=cfg
        ):
            result = await AgentIngestService.extract_structured_data(
                {
                    "raw_text": "fallback text",
                    "structured_content": {"rows": [{"a": 1}]},
                    "source": "csv_local",
                }
            )

        self.assertEqual(result["source"], "fallback")
        self.assertIn("document_summary", result)

    async def test_extract_structured_data_parses_mocked_llm_json(self) -> None:
        cfg = DeepseekConfig(
            api_key="fake-key",
            base_url="https://api.deepseek.com/v1",
            model="deepseek-chat",
            temperature=0.2,
            max_tokens=256,
        )

        with (
            patch(
                "app.api.v1.modules.agent.service.get_deepseek_config",
                return_value=cfg,
            ),
            patch.object(
                AgentIngestService,
                "_call_deepseek_structuring",
                new=AsyncMock(return_value='{"document_summary":"ok","entities":[]}'),
            ),
        ):
            result = await AgentIngestService.extract_structured_data(
                {
                    "raw_text": "something",
                    "structured_content": {},
                    "source": "mineru",
                }
            )

        self.assertEqual(result["document_summary"], "ok")

    async def test_extract_structured_data_csv_maps_all_rows(self) -> None:
        csv_output = {
            "source": "csv_local",
            "raw_text": "",
            "structured_content": {
                "headers": ["PR Name", "Type", "Formulator Name", "Date", "SA"],
                "rows": [
                    {
                        "PR Name": "Test2",
                        "Type": "3D printing",
                        "Formulator Name": "Ana",
                        "Date": "2025/11/6",
                        "SA": "For test",
                    },
                    {
                        "PR Name": "Test3",
                        "Type": "3D printing",
                        "Formulator Name": "Jone",
                        "Date": "2025/11/6",
                        "SA": "For test",
                    },
                    {
                        "PR Name": "Test4",
                        "Type": "3D printing",
                        "Formulator Name": "Ana",
                        "Date": "2025/11/6",
                        "SA": "For test",
                    },
                ],
                "row_count": 3,
            },
        }

        result = await AgentIngestService.extract_structured_data(csv_output)

        self.assertEqual(result["target_table"], "project")
        items = result["domain_data"]["items"]
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]["ProjectName"], "Test2")
        self.assertEqual(items[0]["ProjectTypeName"], "3D Printing")

    async def test_extract_structured_data_csv_maps_raw_materials_rows(self) -> None:
        csv_output = {
            "source": "csv_local",
            "raw_text": "",
            "structured_content": {
                "headers": ["Trade Name", "Supplier", "CAS", "Density"],
                "rows": [
                    {
                        "Trade Name": "Resin-A",
                        "Supplier": "ACME",
                        "CAS": "123-45-6",
                        "Density": "1.11",
                    },
                    {
                        "Trade Name": "Resin-B",
                        "Supplier": "ACME",
                        "CAS": "223-45-6",
                        "Density": "1.20",
                    },
                ],
                "row_count": 2,
            },
        }

        result = await AgentIngestService.extract_structured_data(csv_output)

        self.assertEqual(result["target_table"], "raw_materials")
        items = result["domain_data"]["items"]
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["TradeName"], "Resin-A")

    async def test_extract_structured_data_csv_maps_formula_rows(self) -> None:
        csv_output = {
            "source": "csv_local",
            "raw_text": "",
            "structured_content": {
                "headers": [
                    "PR Name",
                    "Material Name",
                    "Filler Name",
                    "Weight Percentage",
                    "Addition Method",
                ],
                "rows": [
                    {
                        "PR Name": "Test2",
                        "Material Name": "Resin-A",
                        "Filler Name": "Filler-A",
                        "Weight Percentage": "30",
                        "Addition Method": "mix",
                    },
                    {
                        "PR Name": "Test2",
                        "Material Name": "Resin-B",
                        "Filler Name": "Filler-B",
                        "Weight Percentage": "70",
                        "Addition Method": "mix",
                    },
                ],
                "row_count": 2,
            },
        }

        result = await AgentIngestService.extract_structured_data(csv_output)

        self.assertEqual(result["target_table"], "formula_composition")
        items = result["domain_data"]["items"]
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["ProjectName"], "Test2")
        self.assertEqual(items[0]["WeightPercentage"], "30")

    async def test_extract_structured_data_csv_maps_test_result_rows(self) -> None:
        csv_output = {
            "source": "csv_local",
            "raw_text": "",
            "structured_content": {
                "headers": ["PR Name", "Ink_Viscosity", "TestDate", "Notes"],
                "rows": [
                    {
                        "PR Name": "Test2",
                        "Ink_Viscosity": "10cps",
                        "TestDate": "2025/11/6",
                        "Notes": "ok",
                    },
                    {
                        "PR Name": "Test3",
                        "Ink_Viscosity": "11cps",
                        "TestDate": "2025/11/7",
                        "Notes": "ok",
                    },
                ],
                "row_count": 2,
            },
        }

        result = await AgentIngestService.extract_structured_data(csv_output)

        self.assertEqual(result["target_table"], "test_results_ink")
        items = result["domain_data"]["items"]
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["ProjectName"], "Test2")
        self.assertEqual(items[0]["Ink_Viscosity"], "10cps")

    async def test_call_mineru_api_falls_back_to_parse_when_batch_404(self) -> None:
        cfg = MinerUConfig(
            api_url="http://mineru.local",
            api_key="",
            parse_path="/parse",
            timeout_seconds=30,
        )

        with (
            tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as file_obj,
            patch(
                "app.api.v1.modules.agent.service.get_mineru_config", return_value=cfg
            ),
            patch(
                "app.api.v1.modules.agent.service.requests.post",
                return_value=_FakeResponse(status_code=404, text="not found"),
            ),
            patch.object(
                AgentIngestService,
                "_call_mineru_parse_api",
                new=AsyncMock(
                    return_value={
                        "raw_text": "ok",
                        "structured_content": {},
                        "source": "mineru_parse_api",
                    }
                ),
            ) as parse_mock,
        ):
            file_obj.write(b"%PDF-1.4 mock")
            file_path = file_obj.name

            result = await AgentIngestService._call_mineru_api(file_path, "sample.pdf")

        Path(file_path).unlink(missing_ok=True)
        parse_mock.assert_awaited_once()
        self.assertEqual(result["source"], "mineru_parse_api")

    async def test_call_mineru_api_raises_on_poll_404(self) -> None:
        cfg = MinerUConfig(
            api_url="http://mineru.local",
            api_key="",
            parse_path="/parse",
            timeout_seconds=15,
        )

        batch_ok = _FakeResponse(
            status_code=200,
            json_payload={
                "code": 0,
                "data": {
                    "batch_id": "batch-123",
                    "file_urls": ["http://upload.local/presigned"],
                },
            },
        )

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as file_obj:
            file_obj.write(b"%PDF-1.4 mock")
            file_path = file_obj.name

        try:
            with (
                patch(
                    "app.api.v1.modules.agent.service.get_mineru_config",
                    return_value=cfg,
                ),
                patch(
                    "app.api.v1.modules.agent.service.requests.post",
                    return_value=batch_ok,
                ),
                patch(
                    "app.api.v1.modules.agent.service.requests.put",
                    return_value=_FakeResponse(status_code=200),
                ),
                patch(
                    "app.api.v1.modules.agent.service.requests.get",
                    side_effect=[
                        _FakeResponse(status_code=404, text="404 page not found"),
                        _FakeResponse(status_code=404, text="404 page not found"),
                    ],
                ),
                patch(
                    "app.api.v1.modules.agent.service.asyncio.sleep",
                    new=AsyncMock(return_value=None),
                ),
            ):
                with self.assertRaises(ExternalServiceException) as exc_ctx:
                    await AgentIngestService._call_mineru_api(file_path, "sample.pdf")
        finally:
            Path(file_path).unlink(missing_ok=True)

        self.assertIn("Poll endpoint returned 404", str(exc_ctx.exception))

    async def test_call_mineru_api_switches_poll_endpoint_after_batch_404(self) -> None:
        cfg = MinerUConfig(
            api_url="http://mineru.local",
            api_key="",
            parse_path="/parse",
            timeout_seconds=15,
        )

        batch_ok = _FakeResponse(
            status_code=200,
            json_payload={
                "code": 0,
                "data": {
                    "batch_id": "batch-123",
                    "file_urls": ["http://upload.local/presigned"],
                },
            },
        )

        poll_done = _FakeResponse(
            status_code=200,
            json_payload={
                "code": 0,
                "data": {
                    "state": "done",
                    "full_zip_url": "",
                },
            },
        )

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as file_obj:
            file_obj.write(b"%PDF-1.4 mock")
            file_path = file_obj.name

        try:
            with (
                patch(
                    "app.api.v1.modules.agent.service.get_mineru_config",
                    return_value=cfg,
                ),
                patch(
                    "app.api.v1.modules.agent.service.requests.post",
                    return_value=batch_ok,
                ),
                patch(
                    "app.api.v1.modules.agent.service.requests.put",
                    return_value=_FakeResponse(status_code=200),
                ),
                patch(
                    "app.api.v1.modules.agent.service.requests.get",
                    side_effect=[
                        _FakeResponse(status_code=404, text="404 page not found"),
                        poll_done,
                    ],
                ) as get_mock,
                patch(
                    "app.api.v1.modules.agent.service.asyncio.sleep",
                    new=AsyncMock(return_value=None),
                ),
            ):
                result = await AgentIngestService._call_mineru_api(
                    file_path, "sample.pdf"
                )
        finally:
            Path(file_path).unlink(missing_ok=True)

        self.assertEqual(result["source"], "mineru_cloud")
        self.assertIn("structured_content", result)
        first_call_url = get_mock.call_args_list[0].args[0]
        second_call_url = get_mock.call_args_list[1].args[0]
        self.assertIn("/extract-results/batch/", first_call_url)
        self.assertIn("/extract/task/", second_call_url)

    async def test_review_record_rejects_repeated_manual_review(self) -> None:
        record = SimpleNamespace(
            RecordID=88,
            TaskID_FK=23,
            ReviewedByUserID_FK=7,
            ReviewedAt=None,
        )

        with (
            patch(
                "app.api.v1.modules.agent.service.AgentIngestService._ensure_review_role"
            ),
            patch(
                "app.api.v1.modules.agent.service.AgentCRUD.get_ingest_record_by_id",
                new=AsyncMock(return_value=record),
            ),
        ):
            with self.assertRaisesRegex(ValidationException, "already been reviewed"):
                await AgentIngestService.review_record(
                    db=AsyncMock(),
                    record_id=record.RecordID,
                    review_data=AgentReviewUpdateRequest(action="approved"),
                    reviewer_user_id=1,
                    reviewer_role="admin",
                )

    async def test_persist_project_supports_items_batch(self) -> None:
        db = AsyncMock()
        db.execute = AsyncMock(
            return_value=SimpleNamespace(scalar_one_or_none=lambda: None)
        )

        created_projects = [
            SimpleNamespace(ProjectID=101, FormulaCode="PRJ001"),
            SimpleNamespace(ProjectID=102, FormulaCode="PRJ002"),
        ]

        with (
            patch.object(
                AgentIngestService,
                "_find_or_create_project_type",
                new=AsyncMock(return_value=1),
            ),
            patch(
                "app.api.v1.modules.projects.crud.ProjectCRUD.create_project",
                new=AsyncMock(side_effect=created_projects),
            ),
        ):
            result = await AgentIngestService._persist_project(
                db,
                {
                    "items": [
                        {"ProjectName": "A", "ProjectTypeName": "3D printing"},
                        {"ProjectName": "B", "ProjectTypeName": "Inkjet"},
                    ]
                },
            )

        self.assertTrue(result["persisted"])
        self.assertEqual(result["created_count"], 2)
        self.assertEqual(result["created_ids"], [101, 102])


if __name__ == "__main__":
    unittest.main()
