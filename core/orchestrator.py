"""Common orchestration primitives."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from .agent import BaseAgent
from .database import SQLiteDatabase


@dataclass
class OperationResult:
    """Serializable summary of a department run."""

    department: str
    total_items: int = 0
    executed: int = 0
    failed: int = 0
    reports: list[dict[str, Any]] = field(default_factory=list)

    def summary(self) -> dict[str, Any]:
        return {
            "department": self.department,
            "total_items": self.total_items,
            "executed": self.executed,
            "failed": self.failed,
            "reports": self.reports,
        }


class BaseOrchestrator:
    """Execute a sequence of independent agent tasks."""

    department = "core"

    def __init__(self, db: SQLiteDatabase | None = None, agent: BaseAgent | None = None) -> None:
        self.db = db or SQLiteDatabase()
        self.agent = agent or BaseAgent(f"{self.department}-worker")

    def run(self, items: Iterable[dict[str, Any]]) -> OperationResult:
        items = list(items)
        result = OperationResult(self.department, total_items=len(items))
        for item in items:
            try:
                report = self.agent.execute(item)
                self.db.record_operation(self.department, "execute", "completed")
                result.reports.append(report)
                result.executed += 1
            except Exception as exc:  # pragma: no cover - defensive boundary
                self.db.record_operation(self.department, "execute", "failed")
                result.reports.append({"status": "failed", "error": str(exc)})
                result.failed += 1
        return result

    def status(self) -> dict[str, Any]:
        operations = self.db.list_operations(self.department)
        return {"department": self.department, "operations": operations}
