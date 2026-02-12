"""Phase 0 bootstrap tests with LLM/network isolation."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from app.agent.config import DeepseekConfig
from app.agent.core.bootstrap import run_phase0_checks
from app.agent.core.llm import check_deepseek_connectivity
from app.agent.core.react_agent import run_empty_dialogue
from app.agent.tests.mock_llm import MockAgentExecutor, MockAgentExecutorLegacy


class Phase0BootstrapTests(unittest.TestCase):
    def test_connectivity_returns_skipped_without_api_key(self) -> None:
        cfg = DeepseekConfig(
            api_key="",
            base_url="https://api.deepseek.com/v1",
            model="deepseek-chat",
            temperature=0.2,
            max_tokens=256,
        )
        with patch("app.agent.core.llm.get_deepseek_config", return_value=cfg):
            result = check_deepseek_connectivity()
        self.assertEqual(result["status"], "skipped")

    def test_run_empty_dialogue_messages_branch(self) -> None:
        """Primary branch: executor returns messages, parse last content."""
        executor = MockAgentExecutor(output="ok")
        result = run_empty_dialogue(executor)  # type: ignore[arg-type]
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["output"], "ok")
        self.assertIsNotNone(executor.last_payload)

    def test_run_empty_dialogue_legacy_output_branch(self) -> None:
        """Fallback branch: executor returns {"output": ...}."""
        executor = MockAgentExecutorLegacy(output="ok")
        result = run_empty_dialogue(executor)  # type: ignore[arg-type]
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["output"], "ok")
        self.assertIsNotNone(executor.last_payload)

    def test_run_empty_dialogue_empty_messages(self) -> None:
        """Edge case: fallback when messages is an empty list."""
        executor = MockAgentExecutorLegacy(output="fallback")
        # Override invoke to return empty messages
        original_invoke = executor.invoke

        def invoke_empty_messages(payload: dict) -> dict:
            original_invoke(payload)
            return {"messages": [], "output": "fallback"}

        executor.invoke = invoke_empty_messages  # type: ignore[assignment]

        result = run_empty_dialogue(executor)  # type: ignore[arg-type]
        self.assertEqual(result["output"], "fallback")

    def test_phase0_checks_can_skip_live_llm(self) -> None:
        with patch(
            "app.agent.core.bootstrap.check_deepseek_connectivity"
        ) as mock_check:
            mock_check.return_value = {"status": "skipped", "reason": "no key"}
            result = run_phase0_checks(skip_live_llm=True)

        self.assertEqual(result["agent_loop"]["status"], "skipped")


if __name__ == "__main__":
    unittest.main()
