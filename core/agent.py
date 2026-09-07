"""Base agent implementation with structured logging."""

from __future__ import annotations

import logging
from typing import Any


class BaseAgent:
    """Small, dependency-free base class for department agents."""

    def __init__(self, name: str | None = None) -> None:
        self.name = name or self.__class__.__name__
        self.logger = logging.getLogger(f"agents_team.{self.name}")

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Execute a task and return a serializable result."""
        self.logger.info("executing task")
        return {"agent": self.name, "status": "completed", "payload": payload}
