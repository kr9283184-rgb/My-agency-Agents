import os
import tempfile

from website_development.database import WebsiteDatabase
from website_development.orchestrator import WebsiteOrchestrator


def test_website_department_runs_end_to_end():
    tmp_dir = tempfile.mkdtemp()
    db = WebsiteDatabase(os.path.join(tmp_dir, "website.db"))
    orchestrator = WebsiteOrchestrator(db=db)

    project = {
        "project_id": "web-test-001",
        "company_name": "Web Test Co",
        "industry": "hospitality",
        "project_type": "hotel_resort",
        "platform": "nextjs",
    }

    result = orchestrator.run(project=project, output_dir=tmp_dir)

    assert result.total_projects == 1
    assert result.executed == 1
    assert result.failed == 0

    stored = db.get_project("web-test-001")
    assert stored is not None
    assert stored["status"] == "completed"
    assert stored["completion_pct"] == 100.0

    outputs = db.get_outputs("web-test-001")
    assert len(outputs) == 14

    expected = [
        "01_business_analysis_report.md",
        "03_ux_blueprint.md",
        "04_visual_design_system.md",
        "09_seo_report.md",
        "12_qa_approval_report.md",
        "13_deployment_guide.md",
        "14_maintenance_guide.md",
    ]
    for filename in expected:
        path = os.path.join(tmp_dir, "Web_Test_Co", filename)
        assert os.path.isfile(path)
        with open(path) as f:
            assert "Web Test Co" in f.read()


def test_status_summary():
    tmp_dir = tempfile.mkdtemp()
    db = WebsiteDatabase(os.path.join(tmp_dir, "website.db"))
    orchestrator = WebsiteOrchestrator(db=db)
    orchestrator.run(output_dir=tmp_dir)

    status = orchestrator.run_status()
    assert status["summary"]["total_projects"] == 1
    assert status["summary"]["by_status"]["completed"] == 1
