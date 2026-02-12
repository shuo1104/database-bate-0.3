"""Phase 3 unit tests for ML placeholder tool and schemas."""

from __future__ import annotations

import json
import unittest

from app.agent.schemas import (
    MLFeatureSchema,
    MLPredictionInputSchema,
    MLPredictionOutputSchema,
)
from app.agent.tools.ml.predict_tool import (
    _parse_context,
    _parse_features,
    agent_ml_predict_placeholder,
)


# ---------------------------------------------------------------------------
# Schema validation tests
# ---------------------------------------------------------------------------

class MLFeatureSchemaTests(unittest.TestCase):
    def test_valid_feature(self) -> None:
        f = MLFeatureSchema(name="density", value=1.05)
        self.assertEqual(f.name, "density")
        self.assertEqual(f.value, 1.05)
        self.assertIsNone(f.source)

    def test_feature_with_source(self) -> None:
        f = MLFeatureSchema(name="viscosity", value=300, source="database")
        self.assertEqual(f.source, "database")

    def test_empty_name_rejected(self) -> None:
        with self.assertRaises(Exception):
            MLFeatureSchema(name="", value=1)


class MLPredictionInputSchemaTests(unittest.TestCase):
    def test_defaults(self) -> None:
        s = MLPredictionInputSchema()
        self.assertEqual(s.model_name, "default")
        self.assertEqual(s.features, [])
        self.assertEqual(s.context, {})

    def test_with_features(self) -> None:
        s = MLPredictionInputSchema(
            model_name="ink_predictor",
            features=[MLFeatureSchema(name="density", value=1.0)],
        )
        self.assertEqual(len(s.features), 1)
        self.assertEqual(s.features[0].name, "density")


class MLPredictionOutputSchemaTests(unittest.TestCase):
    def test_valid_output(self) -> None:
        o = MLPredictionOutputSchema(
            model_name="test",
            prediction={"result": "good"},
            confidence=0.85,
        )
        self.assertEqual(o.confidence, 0.85)
        self.assertIsNone(o.error)

    def test_confidence_bounds(self) -> None:
        with self.assertRaises(Exception):
            MLPredictionOutputSchema(model_name="test", confidence=1.5)
        with self.assertRaises(Exception):
            MLPredictionOutputSchema(model_name="test", confidence=-0.1)


# ---------------------------------------------------------------------------
# _parse_features tests
# ---------------------------------------------------------------------------

class ParseFeaturesTests(unittest.TestCase):
    def test_empty_string(self) -> None:
        self.assertEqual(_parse_features(""), [])

    def test_json_list_of_dicts(self) -> None:
        result = _parse_features('[{"name": "d", "value": 1}]')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "d")

    def test_json_list_of_scalars(self) -> None:
        result = _parse_features("[1, 2, 3]")
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["name"], "feature_0")
        self.assertEqual(result[0]["value"], 1)

    def test_json_object(self) -> None:
        result = _parse_features('{"density": 1.05, "viscosity": 300}')
        names = {item["name"] for item in result}
        self.assertIn("density", names)
        self.assertIn("viscosity", names)

    def test_invalid_json_raises(self) -> None:
        with self.assertRaises(Exception):
            _parse_features("not json")


# ---------------------------------------------------------------------------
# _parse_context tests
# ---------------------------------------------------------------------------

class ParseContextTests(unittest.TestCase):
    def test_empty_string(self) -> None:
        self.assertEqual(_parse_context(""), {})

    def test_valid_object(self) -> None:
        result = _parse_context('{"project_id": 1}')
        self.assertEqual(result["project_id"], 1)

    def test_non_object_raises(self) -> None:
        with self.assertRaises(ValueError):
            _parse_context("[1, 2, 3]")


# ---------------------------------------------------------------------------
# Tool invocation tests
# ---------------------------------------------------------------------------

class AgentMlPredictPlaceholderTests(unittest.TestCase):
    def test_returns_not_implemented(self) -> None:
        raw = agent_ml_predict_placeholder.invoke(
            {"model_name": "test", "features_json": "[]", "context_json": "{}"}
        )
        result = json.loads(raw)
        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "not_implemented")

    def test_returns_request_preview(self) -> None:
        raw = agent_ml_predict_placeholder.invoke(
            {
                "model_name": "ink_predictor",
                "features_json": '[{"name": "density", "value": 1.0}]',
                "context_json": "{}",
            }
        )
        result = json.loads(raw)
        self.assertEqual(result["request_preview"]["model_name"], "ink_predictor")

    def test_invalid_features_returns_error(self) -> None:
        raw = agent_ml_predict_placeholder.invoke(
            {"model_name": "test", "features_json": "not json", "context_json": "{}"}
        )
        result = json.loads(raw)
        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "invalid_request")

    def test_default_args(self) -> None:
        raw = agent_ml_predict_placeholder.invoke({})
        result = json.loads(raw)
        self.assertIn("status", result)


if __name__ == "__main__":
    unittest.main()
