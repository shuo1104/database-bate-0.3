"""Per-request context for agent tool authorization and scoping."""

from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass


@dataclass(frozen=True)
class AgentRequestContext:
    user_id: int
    user_role: str
    project_scope: list[int] | None
    top_k: int


_AGENT_REQUEST_CONTEXT: ContextVar[AgentRequestContext | None] = ContextVar(
    "agent_request_context",
    default=None,
)


def set_agent_request_context(
    context: AgentRequestContext,
) -> Token[AgentRequestContext | None]:
    return _AGENT_REQUEST_CONTEXT.set(context)


def reset_agent_request_context(token: Token[AgentRequestContext | None]) -> None:
    _AGENT_REQUEST_CONTEXT.reset(token)


def get_agent_request_context() -> AgentRequestContext | None:
    return _AGENT_REQUEST_CONTEXT.get()
