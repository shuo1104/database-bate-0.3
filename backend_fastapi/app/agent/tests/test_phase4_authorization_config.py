"""Phase 4 unit tests for agent authorization config."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from app.agent.config.authorization import get_agent_authorization_config


class Phase4AuthorizationConfigTests(unittest.TestCase):
    def test_role_policy_resolution(self) -> None:
        with (
            patch(
                "app.agent.config.authorization.settings.AGENT_ALLOWED_ROLES",
                ["admin", "user"],
            ),
            patch(
                "app.agent.config.authorization.settings.AGENT_REVIEW_ROLES", ["admin"]
            ),
            patch(
                "app.agent.config.authorization.settings.AGENT_ENFORCE_PROJECT_SCOPE_ROLES",
                ["user"],
            ),
            patch(
                "app.agent.config.authorization.settings.AGENT_MUTATION_ROLES",
                ["admin"],
            ),
            patch(
                "app.agent.config.authorization.settings.AGENT_ADMIN_ROLES",
                ["superadmin"],
            ),
        ):
            cfg = get_agent_authorization_config()

        self.assertTrue(cfg.can_use_agent("admin"))
        self.assertTrue(cfg.can_use_agent("user"))
        self.assertFalse(cfg.can_use_agent("guest"))
        self.assertTrue(cfg.can_review("admin"))
        self.assertFalse(cfg.can_review("user"))
        self.assertTrue(cfg.requires_project_scope("user"))
        self.assertFalse(cfg.requires_project_scope("admin"))
        self.assertTrue(cfg.can_mutate("admin"))
        self.assertFalse(cfg.can_mutate("user"))
        self.assertTrue(cfg.can_admin("superadmin"))
        self.assertFalse(cfg.can_admin("admin"))


if __name__ == "__main__":
    unittest.main()
