import os
import tempfile

from ai_automation.database import AutomationDatabase
from ai_automation.orchestrator import AutomationOrchestrator


def test_automation_department_runs_end_to_end():
    tmp_dir = tempfile.mkdtemp()
    db = AutomationDatabase(os.path.join(tmp_dir, "automation.db"))
    orchestrator = AutomationOrchestrator(db=db)

    project = {
        "project_id": "auto-test-001",
        "company_name": "Automation Test Co",
        "industry": "home services",
        "project_type": "ai_receptionist",
        "priority": "high",
        "timeline": "2 weeks",
        "objectives": "Qualify inbound calls and book appointments automatically.",
    }

    result = orchestrator.run(project=project, output_dir=tmp_dir)

    assert result.total_projects == 1
    assert result.executed == 1
    assert result.failed == 0

    stored = db.get_project("auto-test-001")
    assert stored is not None
    assert stored["status"] == "completed"
    assert stored["completion_pct"] == 100.0

    outputs = db.get_outputs("auto-test-001")
    assert len(outputs) == 15

    expected = [
        "01_automation_execution_plan.md",
        "02_technical_architecture.md",
        "04_workflow_package.md",
        "06_ai_receptionist_system.md",
        "11_testing_report.md",
        "12_security_assessment.md",
        "13_deployment_package.md",
        "15_maintenance_guide.md",
    ]
    for filename in expected:
        path = os.path.join(tmp_dir, "Automation_Test_Co", filename)
        assert os.path.isfile(path)
        with open(path) as f:
            assert "Automation Test Co" in f.read()


def test_status_summary():
    tmp_dir = tempfile.mkdtemp()
    db = AutomationDatabase(os.path.join(tmp_dir, "automation.db"))
    orchestrator = AutomationOrchestrator(db=db)
    orchestrator.run(output_dir=tmp_dir)

    status = orchestrator.run_status()
    assert status["summary"]["total_projects"] == 1
    assert status["summary"]["by_status"]["completed"] == 1
