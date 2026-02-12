"""Phase 0 bootstrap helpers for manual verification."""

from __future__ import annotations

from typing import Any

from app.agent.core.llm import check_deepseek_connectivity
from app.agent.core.react_agent import build_react_agent, run_empty_dialogue


def run_phase0_checks(skip_live_llm: bool = False) -> dict[str, Any]:
    """Run Deepseek connectivity and ReAct loop checks.

    When `skip_live_llm=True`, only return a dry-run result for agent loop wiring.
    """
    connectivity = check_deepseek_connectivity()

    if skip_live_llm:
        loop_result = {
            "status": "skipped",
            "reason": "skip_live_llm=True",
        }
    elif connectivity.get("status") != "ok":
        loop_result = {
            "status": "skipped",
            "reason": "connectivity check not ok",
        }
    else:
        executor = build_react_agent()
        loop_result = run_empty_dialogue(executor)

    return {
        "connectivity": connectivity,
        "agent_loop": loop_result,
    }
