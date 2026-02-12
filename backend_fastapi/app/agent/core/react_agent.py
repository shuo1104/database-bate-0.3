"""LangChain ReAct Agent skeleton for Phase 0."""

from __future__ import annotations

from typing import Any

from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from app.agent.config import get_deepseek_config
from app.agent.tools import get_registered_agent_tools


@tool("no_op")
def no_op(input_text: str) -> str:
    """No-op tool used only for Phase 0 agent-loop bootstrap."""
    return "noop"


def build_langchain_llm() -> BaseLanguageModel:
    cfg = get_deepseek_config()
    return ChatOpenAI(
        # IMPORTANT: api_key must be str, NOT lambda. Do not revert to lambda.
        api_key=cfg.api_key,
        base_url=cfg.base_url,
        model=cfg.model,
        temperature=cfg.temperature,
        max_tokens=cfg.max_tokens,
    )


def build_react_agent(
    llm: BaseLanguageModel | None = None,
    include_ml_tool: bool = False,
) -> Any:
    llm_instance = llm or build_langchain_llm()
    tools = [no_op, *get_registered_agent_tools(include_ml_tool=include_ml_tool)]

    prompt = (
        "You are an internal Agent assistant. "
        "Use document ingest tool when file extraction is needed, "
        "and use text-to-sql tool when user asks structured data questions."
    )

    if include_ml_tool:
        prompt += " Use ML placeholder tool only when user explicitly asks for model prediction."

    return create_react_agent(
        model=llm_instance,
        tools=tools,
        prompt=prompt,
    )


def run_empty_dialogue(executor: Any) -> dict[str, Any]:
    """Run one minimal dialogue round to verify agent loop."""
    result = executor.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Reply with the single token: ok. Do not use tools.",
                }
            ]
        }
    )
    output = ""
    messages = result.get("messages", []) if isinstance(result, dict) else []
    if messages:
        last_message = messages[-1]
        output = getattr(last_message, "content", "") or ""
        if isinstance(output, list):
            output = "".join(str(item) for item in output)
    elif isinstance(result, dict):
        output = str(result.get("output", ""))
    return {
        "status": "ok",
        "output": str(output).strip(),
    }
