import pytest

from core.database import SQLiteDatabase


DEPARTMENTS = [
    "ai_automation",
    "client_outreach",
    "lead_generation",
    "onboarding",
    "project_management",
    "security",
    "testing",
    "web_development",
]


@pytest.mark.parametrize("department", DEPARTMENTS)
def test_department_orchestrator_runs_without_external_services(department):
    module = __import__(f"departments.{department}.orchestrator", fromlist=["Orchestrator"])
    orchestrator = module.Orchestrator(db=SQLiteDatabase(":memory:"))
    result = orchestrator.run([{"task": "smoke"}])
    assert result.department == department
    assert result.executed == 1
    assert result.failed == 0
    assert orchestrator.status()["operations"][0]["department"] == department
