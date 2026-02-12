"""Mock helpers for Agent Phase 0 tests."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MockMessage:
    """Minimal mock that mimics LangChain message objects."""

    content: str
    type: str = "ai"


class MockAgentExecutor:
    """Fake executor returning messages format (primary path of run_empty_dialogue)."""

    def __init__(self, output: str = "ok") -> None:
        self.output = output
        self.last_payload: dict | None = None

    def invoke(self, payload: dict) -> dict:
        self.last_payload = payload
        return {"messages": [MockMessage(content=self.output)]}


class MockAgentExecutorLegacy:
    """Fake executor returning legacy output format (fallback path)."""

    def __init__(self, output: str = "ok") -> None:
        self.output = output
        self.last_payload: dict | None = None

    def invoke(self, payload: dict) -> dict:
        self.last_payload = payload
        return {"output": self.output}
