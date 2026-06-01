import os
import tempfile

from testing_department.database import TestingDatabase
from testing_department.orchestrator import TestingOrchestrator


def test_testing_department_runs_end_to_end():
    tmp_dir = tempfile.mkdtemp()
    db = TestingDatabase(os.path.join(tmp_dir, "testing.db"))
    orchestrator = TestingOrchestrator(db=db)

    project = {
        "qa_id": "qa-test-001",
        "product_name": "QA Test Portal",
        "product_type": "web_application",
        "risk_level": "high",
        "owner": "Delivery Team",
        "requirements": "Validate website, API, AI chatbot, automation, security, and performance.",
        "acceptance_criteria": "No critical bugs and all core flows pass.",
    }

    result = orchestrator.run(project=project, output_dir=tmp_dir)

    assert result.total_projects == 1
    assert result.completed == 1
    assert result.failed == 0

    stored = db.get_project("qa-test-001")
    assert stored is not None
    assert stored["status"] == "completed"
    assert stored["completion_pct"] == 100.0
    assert stored["quality_score"] == 80.0
    assert stored["qa_decision"] == "Pass With Issues"

    outputs = db.get_outputs("qa-test-001")
    assert len(outputs) == 14

    bugs = db.get_bugs("qa-test-001")
    assert len(bugs) == 2

    expected = [
        "01_final_qa_decision.md",
        "02_requirement_validation_report.md",
        "03_functional_testing_report.md",
        "05_ai_quality_report.md",
        "08_performance_report.md",
        "09_security_verification_report.md",
        "14_release_approval_certificate.md",
    ]
    for filename in expected:
        path = os.path.join(tmp_dir, "QA_Test_Portal", filename)
        assert os.path.isfile(path)
        with open(path) as f:
            assert "QA Test Portal" in f.read()


def test_status_summary():
    tmp_dir = tempfile.mkdtemp()
    db = TestingDatabase(os.path.join(tmp_dir, "testing.db"))
    orchestrator = TestingOrchestrator(db=db)
    orchestrator.run(output_dir=tmp_dir)

    status = orchestrator.run_status()
    assert status["summary"]["total_projects"] == 1
    assert status["summary"]["by_status"]["completed"] == 1
    assert status["summary"]["bugs"]["medium"] == 1
