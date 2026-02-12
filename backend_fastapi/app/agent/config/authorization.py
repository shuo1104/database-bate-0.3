"""Agent authorization policy wrappers."""

from __future__ import annotations

from dataclasses import dataclass

from app.config.settings import settings


@dataclass(frozen=True)
class AgentAuthorizationConfig:
    allowed_roles: set[str]
    review_roles: set[str]
    enforce_project_scope_roles: set[str]
    mutation_roles: set[str]
    admin_roles: set[str]

    def can_use_agent(self, role: str) -> bool:
        return role in self.allowed_roles

    def can_review(self, role: str) -> bool:
        return role in self.review_roles

    def requires_project_scope(self, role: str) -> bool:
        return role in self.enforce_project_scope_roles

    def can_mutate(self, role: str) -> bool:
        return role in self.mutation_roles

    def can_admin(self, role: str) -> bool:
        return role in self.admin_roles


def _normalize_roles(raw_roles: list[str]) -> set[str]:
    return {str(role).strip() for role in raw_roles if str(role).strip()}


def get_agent_authorization_config() -> AgentAuthorizationConfig:
    allowed_roles = _normalize_roles(settings.AGENT_ALLOWED_ROLES or ["admin", "user"])
    review_roles = _normalize_roles(settings.AGENT_REVIEW_ROLES or ["admin"])
    enforce_scope_roles = _normalize_roles(
        settings.AGENT_ENFORCE_PROJECT_SCOPE_ROLES or ["user"]
    )
    mutation_roles = _normalize_roles(settings.AGENT_MUTATION_ROLES or ["admin"])
    admin_roles = _normalize_roles(settings.AGENT_ADMIN_ROLES or ["superadmin"])

    if not allowed_roles:
        allowed_roles = {"admin", "user"}
    if not review_roles:
        review_roles = {"admin"}
    if not mutation_roles:
        mutation_roles = {"admin"}
    if not admin_roles:
        admin_roles = {"superadmin"}

    return AgentAuthorizationConfig(
        allowed_roles=allowed_roles,
        review_roles=review_roles,
        enforce_project_scope_roles=enforce_scope_roles,
        mutation_roles=mutation_roles,
        admin_roles=admin_roles,
    )
