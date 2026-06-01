import os
import tempfile

from security_department.database import SecurityDatabase
from security_department.orchestrator import SecurityOrchestrator


def test_security_department_runs_end_to_end():
    tmp_dir = tempfile.mkdtemp()
    db = SecurityDatabase(os.path.join(tmp_dir, "security.db"))
    orchestrator = SecurityOrchestrator(db=db)

    assessment = {
        "assessment_id": "sec-test-001",
        "target_name": "Security Test Portal",
        "target_type": "web_application",
        "assessment_type": "security_review",
        "risk_level": "high",
        "owner": "Platform Team",
        "scope": "Review app, API, database, AI agents, backups, monitoring, and incident response.",
    }

    result = orchestrator.run(assessment=assessment, output_dir=tmp_dir)

    assert result.total_assessments == 1
    assert result.completed == 1
    assert result.failed == 0

    stored = db.get_assessment("sec-test-001")
    assert stored is not None
    assert stored["status"] == "completed"
    assert stored["completion_pct"] == 100.0
    assert stored["security_score"] == 66.0

    outputs = db.get_outputs("sec-test-001")
    assert len(outputs) == 14

    vulnerabilities = db.get_vulnerabilities("sec-test-001")
    assert len(vulnerabilities) == 3

    expected = [
        "01_executive_security_summary.md",
        "03_application_security_report.md",
        "04_vulnerability_register.md",
        "08_incident_response_report.md",
        "10_ai_security_report.md",
        "11_recovery_readiness_report.md",
        "14_system_reliability_report.md",
    ]
    for filename in expected:
        path = os.path.join(tmp_dir, "Security_Test_Portal", filename)
        assert os.path.isfile(path)
        with open(path) as f:
            assert "Security Test Portal" in f.read()


def test_status_summary():
    tmp_dir = tempfile.mkdtemp()
    db = SecurityDatabase(os.path.join(tmp_dir, "security.db"))
    orchestrator = SecurityOrchestrator(db=db)
    orchestrator.run(output_dir=tmp_dir)

    status = orchestrator.run_status()
    assert status["summary"]["total_assessments"] == 1
    assert status["summary"]["by_status"]["completed"] == 1
    assert status["summary"]["vulnerabilities"]["high"] == 1
