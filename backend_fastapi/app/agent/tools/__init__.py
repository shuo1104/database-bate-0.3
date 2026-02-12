"""LangChain tools exposed to the Agent."""

from app.agent.tools.etl import agent_document_ingest
from app.agent.tools.ml import agent_ml_predict_placeholder
from app.agent.tools.sql import agent_text_to_sql


def get_registered_agent_tools(include_ml_tool: bool = False) -> list:
    tools = [agent_document_ingest, agent_text_to_sql]
    if include_ml_tool:
        tools.append(agent_ml_predict_placeholder)
    return tools


__all__ = [
    "agent_document_ingest",
    "agent_text_to_sql",
    "agent_ml_predict_placeholder",
    "get_registered_agent_tools",
]
