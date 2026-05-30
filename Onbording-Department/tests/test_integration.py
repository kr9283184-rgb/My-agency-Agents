import os
import sqlite3
import tempfile
import json
from onboarding_department.database import OnboardingDatabase
from onboarding_department.orchestrator import OnboardingOrchestrator


def _create_mock_outreach_db(db_path: str):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            lead_id TEXT PRIMARY KEY,
            company_name TEXT NOT NULL,
            contact_name TEXT DEFAULT '',
            email TEXT DEFAULT '',
            whatsapp_phone TEXT DEFAULT '',
            industry TEXT DEFAULT '',
            website TEXT DEFAULT '',
            location TEXT DEFAULT '',
            pipeline_stage TEXT DEFAULT 'New Lead',
            lead_score INTEGER DEFAULT 0,
            notes TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS proposals (
            proposal_id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id TEXT NOT NULL,
            title TEXT NOT NULL,
            proposal_type TEXT DEFAULT 'service',
            amount REAL DEFAULT 0.0,
            status TEXT DEFAULT 'draft',
            sent_at TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS communications (
            comm_id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id TEXT NOT NULL,
            channel TEXT NOT NULL,
            direction TEXT NOT NULL,
            subject TEXT DEFAULT '',
            body TEXT DEFAULT '',
            status TEXT DEFAULT 'sent',
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.execute("""
        INSERT INTO leads (lead_id, company_name, contact_name, email, whatsapp_phone,
                           industry, website, location, pipeline_stage, lead_score, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "integration-test-001",
        "Integration Test Co",
        "Jane Smith",
        "jane@integrationtest.com",
        "+1987654321",
        "technology",
        "https://integrationtest.com",
        "New York, NY",
        "Won",
        95,
        '{"service_fit": "high", "pain_points": ["needs website redesign"]}',
    ))

    conn.execute("""
        INSERT INTO proposals (lead_id, title, proposal_type, amount, status, sent_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "integration-test-001",
        "Website Redesign Proposal",
        "website",
        7500.00,
        "accepted",
        "2026-05-28T10:00:00",
    ))

    conn.execute("""
        INSERT INTO communications (lead_id, channel, direction, subject, body, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "integration-test-001",
        "email",
        "outbound",
        "Introduction",
        "Hello, we can help you...",
        "sent",
    ))

    conn.commit()
    conn.close()


class TestFullPipeline:
    def setup_method(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.outreach_db_path = os.path.join(self.tmp_dir, "outreach.db")
        self.onboarding_db_path = os.path.join(self.tmp_dir, "onboarding.db")
        self.output_dir = os.path.join(self.tmp_dir, "onboarding_output")

        _create_mock_outreach_db(self.outreach_db_path)

        os.environ["OUTREACH_DB_PATH"] = self.outreach_db_path
        os.environ["ONBOARDING_OUTPUT_DIR"] = self.output_dir

        self.db = OnboardingDatabase(self.onboarding_db_path)
        self.orchestrator = OnboardingOrchestrator(db=self.db)

    def teardown_method(self):
        for key in ["OUTREACH_DB_PATH", "ONBOARDING_OUTPUT_DIR"]:
            os.environ.pop(key, None)

    def test_full_pipeline_discovers_won_lead(self):
        leads = self.db.get_won_leads_from_outreach()
        assert len(leads) == 1
        assert leads[0]["lead_id"] == "integration-test-001"
        assert leads[0]["company_name"] == "Integration Test Co"

    def test_full_pipeline_fetches_proposal(self):
        proposal = self.db.get_proposal_from_outreach("integration-test-001")
        assert proposal is not None
        assert proposal["amount"] == 7500.0
        assert proposal["proposal_type"] == "website"

    def test_full_pipeline_runs_end_to_end(self):
        result = self.orchestrator.run(output_dir=self.output_dir)

        assert result.total_leads == 1
        assert result.onboarded == 1
        assert result.failed == 0
        assert len(result.reports) == 1
        assert result.reports[0]["status"] == "completed"

        lead_dir = os.path.join(self.output_dir, "Integration_Test_Co")
        assert os.path.isdir(lead_dir), f"Output directory {lead_dir} not found"

        expected_files = [
            "01_welcome_package.md",
            "02_client_requirement_document.md",
            "03_questionnaire.md",
            "04_asset_request_form.md",
            "05_access_checklist.md",
            "06_brand_analysis_report.md",
            "07_project_scope_document.md",
            "08_contract_verification.md",
            "09_project_roadmap.md",
            "10_development_handover_package.md",
            "11_executive_onboarding_report.md",
        ]
        for fname in expected_files:
            fpath = os.path.join(lead_dir, fname)
            assert os.path.isfile(fpath), f"Missing expected file: {fpath}"
            with open(fpath) as f:
                content = f.read()
                assert "Integration Test Co" in content, f"{fname} missing company name"

    def test_onboarding_db_tracks_progress(self):
        self.orchestrator.run(output_dir=self.output_dir)

        lead = self.db.get_lead("integration-test-001")
        assert lead is not None
        assert lead["status"] == "completed"
        assert lead["welcome_sent_at"] is not None
        assert lead["requirements_collected_at"] is not None
        assert lead["scope_defined_at"] is not None
        assert lead["handover_completed_at"] is not None

    def test_onboarding_db_stores_outputs(self):
        self.orchestrator.run(output_dir=self.output_dir)

        outputs = self.db.get_outputs("integration-test-001")
        output_types = [o["output_type"] for o in outputs]
        expected_types = [
            "questionnaire", "requirements", "assets", "access",
            "brand", "scope", "contract", "roadmap", "handover", "report",
        ]
        for t in expected_types:
            assert t in output_types, f"Missing output type: {t}"

    def test_full_pipeline_status_command(self):
        self.orchestrator.run(output_dir=self.output_dir)

        status = self.orchestrator.run_status()
        assert "leads" in status
        assert len(status["leads"]) == 1
        assert status["leads"][0]["company"] == "Integration Test Co"
        assert status["leads"][0]["current_stage"] == "completed"

    def test_update_outreach_pipeline(self):
        self.orchestrator.run(output_dir=self.output_dir)

        import sqlite3
        conn = sqlite3.connect(self.outreach_db_path)
        row = conn.execute(
            "SELECT pipeline_stage FROM leads WHERE lead_id = ?",
            ("integration-test-001",),
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == "Planning"


class TestMultipleLeads:
    def setup_method(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.outreach_db_path = os.path.join(self.tmp_dir, "outreach.db")
        self.onboarding_db_path = os.path.join(self.tmp_dir, "onboarding.db")
        self.output_dir = os.path.join(self.tmp_dir, "onboarding_output")

        _create_mock_outreach_db(self.outreach_db_path)

        conn = sqlite3.connect(self.outreach_db_path)
        conn.execute("""
            INSERT INTO leads (lead_id, company_name, contact_name, email, industry,
                               pipeline_stage, lead_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("integration-test-002", "Second Corp", "Bob", "bob@second.com", "finance", "Won", 80))
        conn.execute("""
            INSERT INTO proposals (lead_id, title, proposal_type, amount, status)
            VALUES (?, ?, ?, ?, ?)
        """, ("integration-test-002", "Automation Proposal", "automation", 12000, "accepted"))
        conn.commit()
        conn.close()

        os.environ["OUTREACH_DB_PATH"] = self.outreach_db_path
        os.environ["ONBOARDING_OUTPUT_DIR"] = self.output_dir
        self.db = OnboardingDatabase(self.onboarding_db_path)
        self.orchestrator = OnboardingOrchestrator(db=self.db)

    def teardown_method(self):
        for key in ["OUTREACH_DB_PATH", "ONBOARDING_OUTPUT_DIR"]:
            os.environ.pop(key, None)

    def test_onboards_multiple_leads(self):
        result = self.orchestrator.run(output_dir=self.output_dir)
        assert result.total_leads == 2
        assert result.onboarded == 2
        assert result.failed == 0

        for name in ["Integration_Test_Co", "Second_Corp"]:
            lead_dir = os.path.join(self.output_dir, name)
            assert os.path.isdir(lead_dir), f"Missing dir: {lead_dir}"

    def test_handover_destination_differs_by_proposal_type(self):
        self.orchestrator.run(output_dir=self.output_dir)

        for report in self.orchestrator.run().reports:
            pass

        handover_dir = os.path.join(self.output_dir, "Second_Corp")
        handover_file = os.path.join(handover_dir, "10_development_handover_package.md")
        if os.path.isfile(handover_file):
            with open(handover_file) as f:
                content = f.read()
                assert "AI Automation Department" in content
