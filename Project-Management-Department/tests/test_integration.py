import os
import sqlite3
import tempfile
from project_management.database import ProjectDatabase
from project_management.orchestrator import ProjectOrchestrator
from project_management.agents.planning_agent import PlanningAgent
from project_management.agents.resource_allocation_agent import ResourceAllocationAgent


def _create_mock_onboarding_db(db_path: str):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS onboarding_progress (
            lead_id TEXT PRIMARY KEY,
            company_name TEXT NOT NULL,
            contact_name TEXT DEFAULT '',
            email TEXT DEFAULT '',
            whatsapp_phone TEXT DEFAULT '',
            industry TEXT DEFAULT '',
            proposal_type TEXT DEFAULT '',
            deal_amount REAL DEFAULT 0.0,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS onboarding_outputs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id TEXT NOT NULL,
            output_type TEXT NOT NULL,
            file_path TEXT NOT NULL,
            content_preview TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (lead_id) REFERENCES onboarding_progress(lead_id)
        )
    """)

    conn.execute("""
        INSERT INTO onboarding_progress (lead_id, company_name, contact_name, email,
                                          industry, proposal_type, deal_amount, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "integration-lead-001", "Integration Test Co", "Jane Smith",
        "jane@integrationtest.com", "technology", "website", 7500.0, "completed"
    ))

    conn.execute("""
        INSERT INTO onboarding_outputs (lead_id, output_type, file_path)
        VALUES (?, ?, ?)
    """, ("integration-lead-001", "handover", "/tmp/handover_test.md"))

    conn.execute("""
        INSERT INTO onboarding_progress (lead_id, company_name, contact_name, email,
                                          industry, proposal_type, deal_amount, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "integration-lead-002", "Second Automation Inc", "Bob Smith",
        "bob@second.com", "finance", "automation", 12000.0, "completed"
    ))

    conn.execute("""
        INSERT INTO onboarding_outputs (lead_id, output_type, file_path)
        VALUES (?, ?, ?)
    """, ("integration-lead-002", "handover", "/tmp/handover2_test.md"))

    conn.commit()
    conn.close()


class TestFullPipeline:
    def setup_method(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.onboarding_db_path = os.path.join(self.tmp_dir, "onboarding.db")
        self.pm_db_path = os.path.join(self.tmp_dir, "pm.db")
        self.output_dir = os.path.join(self.tmp_dir, "pm_output")

        _create_mock_onboarding_db(self.onboarding_db_path)

        os.environ["ONBOARDING_DB_PATH"] = self.onboarding_db_path
        os.environ["PM_OUTPUT_DIR"] = self.output_dir

        self.db = ProjectDatabase(self.pm_db_path)
        self.orchestrator = ProjectOrchestrator(db=self.db)

    def teardown_method(self):
        for key in ["ONBOARDING_DB_PATH", "PM_OUTPUT_DIR"]:
            os.environ.pop(key, None)

    def test_pipeline_discovers_onboarding_projects(self):
        projects = self.db.get_completed_onboarding_projects()
        assert len(projects) == 2
        assert projects[0]["company_name"] == "Integration Test Co"

    def test_pipeline_runs_end_to_end(self):
        result = self.orchestrator.run(output_dir=self.output_dir)

        assert result.total_projects == 2
        assert result.executed == 2
        assert result.failed == 0
        assert len(result.reports) == 2
        assert result.reports[0]["status"] == "completed"

    def test_pipeline_creates_output_files(self):
        self.orchestrator.run(output_dir=self.output_dir)

        for name in ["Integration_Test_Co", "Second_Automation_Inc"]:
            lead_dir = os.path.join(self.output_dir, name)
            assert os.path.isdir(lead_dir), f"Output directory {lead_dir} not found"

            expected_files = [
                "01_master_project_plan.md",
                "02_resource_assignment_report.md",
                "03_task_dashboard.md",
                "04_coordination_report.md",
                "05_daily_progress_report.md",
                "06_risk_register.md",
                "08_budget_health_report.md",
                "09_client_communication.md",
                "10_qa_readiness_report.md",
                "11_project_delivery_package.md",
                "12_knowledge_base_update.md",
            ]

            found_files = os.listdir(lead_dir)
            for fname in expected_files:
                fpath = os.path.join(lead_dir, fname)
                assert os.path.isfile(fpath), f"Missing expected file: {fpath}"
                with open(fpath) as f:
                    content = f.read()
                    company_name = name.replace("_", " ")
                    assert company_name in content or "Test" in content, f"{fname} missing company name reference"

    def test_pipeline_tracks_progress_in_db(self):
        self.orchestrator.run(output_dir=self.output_dir)

        projects = self.db.get_projects()
        assert len(projects) == 2

        for p in projects:
            assert p["status"] in ("completed", "delivery_ready", "in_progress")
            assert p["completion_pct"] >= 0

    def test_pipeline_tasks_are_created(self):
        self.orchestrator.run(output_dir=self.output_dir)

        for p in self.db.get_projects():
            tasks = self.db.get_tasks(p["project_id"])
            assert len(tasks) > 0, f"No tasks for {p['company_name']}"

    def test_pipeline_milestones_are_created(self):
        self.orchestrator.run(output_dir=self.output_dir)

        for p in self.db.get_projects():
            milestones = self.db.get_milestones(p["project_id"])
            assert len(milestones) == 5, f"Expected 5 milestones for {p['company_name']}, got {len(milestones)}"

    def test_pipeline_budget_tracked(self):
        self.orchestrator.run(output_dir=self.output_dir)

        for p in self.db.get_projects():
            budget = self.db.get_budget_summary(p["project_id"])
            assert budget["deal_amount"] > 0
            assert budget["budget_health"] in ("healthy", "over_budget")

    def test_pipeline_quality_checkpoints_created(self):
        self.orchestrator.run(output_dir=self.output_dir)

        for p in self.db.get_projects():
            qa = self.db.get_qa_readiness(p["project_id"])
            assert qa["total"] > 0

    def test_pipeline_risks_identified(self):
        self.orchestrator.run(output_dir=self.output_dir)

        for p in self.db.get_projects():
            risks = self.db.get_risks(p["project_id"])
            assert len(risks) > 0

    def test_pipeline_knowledge_captured(self):
        self.orchestrator.run(output_dir=self.output_dir)

        for p in self.db.get_projects():
            lessons = self.db.get_lessons(p["project_id"])
            assert len(lessons) > 0

    def test_pipeline_status_command(self):
        self.orchestrator.run(output_dir=self.output_dir)

        status = self.orchestrator.run_status()
        assert "projects" in status
        assert "portfolio" in status
        assert "summary" in status
        assert len(status["projects"]) == 2

    def test_pipeline_specific_project(self):
        self.orchestrator.run(output_dir=self.output_dir)

        projects = self.db.get_projects()
        first_id = projects[0]["project_id"]
        status = self.orchestrator.run_status(first_id)
        assert "project" in status
        assert status["project"]["project_id"] == first_id

    def test_change_request_workflow(self):
        self.orchestrator.run(output_dir=self.output_dir)
        projects = self.db.get_projects()
        first_id = projects[0]["project_id"]

        cr = self.orchestrator.process_change_request(first_id, {
            "title": "Add Feature",
            "description": "Add new feature",
            "estimated_hours": 16,
            "complexity": "medium",
        }, self.output_dir)

        assert "change_request" in cr
        assert cr["change_request"]["status"] == "pending"
        assert cr["impact"]["effort_hours"] > 0

    def test_weekly_report(self):
        self.orchestrator.run(output_dir=self.output_dir)
        projects = self.db.get_projects()
        first_id = projects[0]["project_id"]

        report = self.orchestrator.run_weekly_report(first_id, self.output_dir)
        assert report.get("report_type") == "weekly"
        assert report.get("file_path")


class TestMultipleProjectTypes:
    def setup_method(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp_dir, "test_pm.db")
        self.output_dir = os.path.join(self.tmp_dir, "pm_output")
        self.db = ProjectDatabase(self.db_path)

        website_project = {
            "project_id": "web-001",
            "lead_id": "lead-web",
            "company_name": "Website Client",
            "contact_name": "Alice",
            "email": "alice@web.com",
            "proposal_type": "website",
            "deal_amount": 8000.0,
            "status": "planning",
        }
        automation_project = {
            "project_id": "auto-001",
            "lead_id": "lead-auto",
            "company_name": "Automation Client",
            "contact_name": "Bob",
            "email": "bob@auto.com",
            "proposal_type": "automation",
            "deal_amount": 15000.0,
            "status": "planning",
        }
        self.db.add_project(website_project)
        self.db.add_project(automation_project)

    def test_different_project_types_get_different_plans(self):
        planning = PlanningAgent(db=self.db)
        web_plan = planning.create_project_plan(self.db.get_project("web-001"), self.output_dir)
        auto_plan = planning.create_project_plan(self.db.get_project("auto-001"), self.output_dir)

        web_tasks = self.db.get_tasks("web-001")
        auto_tasks = self.db.get_tasks("auto-001")

        web_titles = [t["title"] for t in web_tasks]
        auto_titles = [t["title"] for t in auto_tasks]

        assert any("Wireframe" in t for t in web_titles), "Website should have design tasks"
        assert any("Workflow" in t for t in auto_titles), "Automation should have workflow tasks"

    def test_different_project_types_get_different_resources(self):
        resource = ResourceAllocationAgent(db=self.db)
        web_res = resource.allocate_resources(self.db.get_project("web-001"), self.output_dir)
        auto_res = resource.allocate_resources(self.db.get_project("auto-001"), self.output_dir)

        assert "Website" in web_res["department"]
        assert "Automation" in auto_res["department"]
