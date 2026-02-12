"""Phase 4 unit tests for AgentAuditCallbackHandler."""

from __future__ import annotations

import time
import unittest
from uuid import uuid4

from app.agent.core.audit_callback import AgentAuditCallbackHandler


class AuditCallbackToolStartTests(unittest.TestCase):
    def test_on_tool_start_records_event(self) -> None:
        handler = AgentAuditCallbackHandler()
        run_id = uuid4()
        handler.on_tool_start(
            serialized={"name": "agent_text_to_sql"},
            input_str='{"question": "query projects"}',
            run_id=run_id,
        )
        self.assertEqual(len(handler.events), 1)
        event = handler.events[0]
        self.assertEqual(event["tool_name"], "agent_text_to_sql")
        self.assertEqual(event["status"], "started")
        self.assertIn("query projects", event["tool_input"])

    def test_tool_name_fallback_to_id(self) -> None:
        handler = AgentAuditCallbackHandler()
        handler.on_tool_start(
            serialized={"id": "tool_123"},
            input_str="test",
            run_id=uuid4(),
        )
        self.assertEqual(handler.events[0]["tool_name"], "tool_123")

    def test_tool_name_fallback_to_unknown(self) -> None:
        handler = AgentAuditCallbackHandler()
        handler.on_tool_start(
            serialized={},
            input_str="test",
            run_id=uuid4(),
        )
        self.assertEqual(handler.events[0]["tool_name"], "unknown_tool")


class AuditCallbackToolEndTests(unittest.TestCase):
    def test_on_tool_end_records_ok_status(self) -> None:
        handler = AgentAuditCallbackHandler()
        run_id = uuid4()
        handler.on_tool_start(
            serialized={"name": "test_tool"},
            input_str="input",
            run_id=run_id,
        )
        handler.on_tool_end(output="result_output", run_id=run_id)

        end_event = handler.events[-1]
        self.assertEqual(end_event["status"], "ok")
        self.assertIn("result_output", end_event["tool_output"])
        self.assertIsNotNone(end_event["duration_ms"])
        self.assertGreaterEqual(end_event["duration_ms"], 0)

    def test_duration_ms_without_start(self) -> None:
        handler = AgentAuditCallbackHandler()
        handler.on_tool_end(output="orphan", run_id=uuid4())
        self.assertIsNone(handler.events[-1]["duration_ms"])


class AuditCallbackToolErrorTests(unittest.TestCase):
    def test_on_tool_error_records_failed_status(self) -> None:
        handler = AgentAuditCallbackHandler()
        run_id = uuid4()
        handler.on_tool_start(
            serialized={"name": "failing_tool"},
            input_str="bad input",
            run_id=run_id,
        )
        handler.on_tool_error(error=ValueError("something broke"), run_id=run_id)

        error_event = handler.events[-1]
        self.assertEqual(error_event["status"], "failed")
        self.assertIn("ValueError", error_event["error"])
        self.assertIn("something broke", error_event["error"])
        self.assertIsNotNone(error_event["duration_ms"])


class AuditCallbackTruncateTests(unittest.TestCase):
    def test_short_value_not_truncated(self) -> None:
        result = AgentAuditCallbackHandler._truncate("short")
        self.assertEqual(result, "short")

    def test_long_value_truncated(self) -> None:
        long_text = "x" * 2000
        result = AgentAuditCallbackHandler._truncate(long_text, limit=100)
        self.assertEqual(len(result), 103)  # 100 + "..."
        self.assertTrue(result.endswith("..."))

    def test_custom_limit(self) -> None:
        result = AgentAuditCallbackHandler._truncate("abcdef", limit=3)
        self.assertEqual(result, "abc...")


class AuditCallbackMultiToolTests(unittest.TestCase):
    def test_multiple_tools_tracked_independently(self) -> None:
        handler = AgentAuditCallbackHandler()
        run_1 = uuid4()
        run_2 = uuid4()

        handler.on_tool_start(
            serialized={"name": "tool_a"}, input_str="a", run_id=run_1
        )
        handler.on_tool_start(
            serialized={"name": "tool_b"}, input_str="b", run_id=run_2
        )
        handler.on_tool_end(output="result_b", run_id=run_2)
        handler.on_tool_end(output="result_a", run_id=run_1)

        self.assertEqual(len(handler.events), 4)
        # run_2 end should come before run_1 end
        self.assertEqual(handler.events[2]["run_id"], str(run_2))
        self.assertEqual(handler.events[3]["run_id"], str(run_1))

    def test_duration_timing_is_reasonable(self) -> None:
        handler = AgentAuditCallbackHandler()
        run_id = uuid4()
        handler.on_tool_start(
            serialized={"name": "slow_tool"}, input_str="x", run_id=run_id
        )
        time.sleep(0.05)  # 50ms
        handler.on_tool_end(output="done", run_id=run_id)

        end_event = handler.events[-1]
        self.assertIsNotNone(end_event["duration_ms"])
        self.assertGreaterEqual(end_event["duration_ms"], 30)  # at least 30ms


if __name__ == "__main__":
    unittest.main()
