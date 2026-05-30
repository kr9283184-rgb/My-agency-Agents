import os
import tempfile
from onboarding_department.database import OnboardingDatabase
from onboarding_department.agents.welcome_agent import WelcomeAgent
from onboarding_department.agents.requirement_agent import RequirementAgent
from onboarding_department.agents.questionnaire_agent import QuestionnaireAgent
from onboarding_department.agents.asset_agent import AssetAgent
from onboarding_department.agents.access_agent import AccessAgent
from onboarding_department.agents.brand_agent import BrandAgent
from onboarding_department.agents.scope_agent import ScopeAgent
from onboarding_department.agents.contract_agent import ContractAgent
from onboarding_department.agents.planning_agent import PlanningAgent
from onboarding_department.agents.handover_agent import HandoverAgent
from onboarding_department.agents.crm_agent import CRMAgent
from onboarding_department.agents.executive_report_agent import ExecutiveReportAgent


SAMPLE_LEAD = {
    "lead_id": "test-001",
    "company_name": "Test Company",
    "contact_name": "John Doe",
    "email": "john@test.com",
    "whatsapp_phone": "+1234567890",
    "industry": "technology",
    "website": "https://testcompany.com",
    "location": "San Francisco, CA",
    "proposal_type": "website",
    "deal_amount": 5000.0,
    "notes": "",
}


class TestAgentBase:
    def setup_method(self):
        self.tmp_dir = tempfile.mkdtemp()
        db_path = os.path.join(self.tmp_dir, "test_onboarding.db")
        self.db = OnboardingDatabase(db_path)

    def teardown_method(self):
        pass


class TestWelcomeAgent(TestAgentBase):
    def test_send_welcome_package(self):
        agent = WelcomeAgent(db=self.db)
        result = agent.send_welcome_package(SAMPLE_LEAD, self.tmp_dir)
        assert "file_path" in result
        assert result["file_path"]
        assert os.path.isfile(result["file_path"])
        with open(result["file_path"]) as f:
            content = f.read()
            assert "Test Company" in content
            assert "John Doe" in content
            assert "Welcome Package" in content


class TestRequirementAgent(TestAgentBase):
    def test_collect_requirements_website(self):
        agent = RequirementAgent(db=self.db)
        result = agent.collect_requirements(SAMPLE_LEAD, {"proposal_type": "website", "amount": 5000}, self.tmp_dir)
        assert result["file_path"]
        assert os.path.isfile(result["file_path"])
        assert result["details"]["project_type"] == "website"
        with open(result["file_path"]) as f:
            content = f.read()
            assert "Test Company" in content

    def test_collect_requirements_automation(self):
        lead = dict(SAMPLE_LEAD, proposal_type="automation")
        agent = RequirementAgent(db=self.db)
        result = agent.collect_requirements(lead, {"proposal_type": "automation"}, self.tmp_dir)
        assert result["details"]["project_type"] == "automation"

    def test_collect_requirements_no_proposal(self):
        agent = RequirementAgent(db=self.db)
        result = agent.collect_requirements(SAMPLE_LEAD, None, self.tmp_dir)
        assert result["file_path"]


class TestQuestionnaireAgent(TestAgentBase):
    def test_generate_questionnaire(self):
        agent = QuestionnaireAgent(db=self.db)
        result = agent.generate_questionnaire(SAMPLE_LEAD, self.tmp_dir)
        assert result["file_path"]
        assert os.path.isfile(result["file_path"])
        with open(result["file_path"]) as f:
            content = f.read()
            assert "Test Company" in content
            assert "John Doe" in content
            assert "Questionnaire" in content


class TestAssetAgent(TestAgentBase):
    def test_collect_assets(self):
        agent = AssetAgent(db=self.db)
        result = agent.collect_assets(SAMPLE_LEAD, self.tmp_dir)
        assert result["file_path"]
        assert os.path.isfile(result["file_path"])
        with open(result["file_path"]) as f:
            content = f.read()
            assert "Test Company" in content
            assert "Logo" in content


class TestAccessAgent(TestAgentBase):
    def test_track_access(self):
        agent = AccessAgent(db=self.db)
        result = agent.track_access(SAMPLE_LEAD, self.tmp_dir)
        assert result["file_path"]
        assert os.path.isfile(result["file_path"])
        with open(result["file_path"]) as f:
            content = f.read()
            assert "Test Company" in content


class TestBrandAgent(TestAgentBase):
    def test_analyze_brand(self):
        agent = BrandAgent(db=self.db)
        result = agent.analyze_brand(SAMPLE_LEAD, self.tmp_dir)
        assert result["file_path"]
        assert os.path.isfile(result["file_path"])
        assert result["summary"]
        assert result["competitor_analysis"]
        assert result["design_recommendations"]
        with open(result["file_path"]) as f:
            content = f.read()
            assert "Brand Analysis" in content


class TestScopeAgent(TestAgentBase):
    def test_define_scope(self):
        agent = ScopeAgent(db=self.db)
        result = agent.define_scope(SAMPLE_LEAD, {}, self.tmp_dir)
        assert result["file_path"]
        assert os.path.isfile(result["file_path"])
        assert "included_features" in result["details"]
        assert "risks" in result["details"]

    def test_define_scope_automation(self):
        agent = ScopeAgent(db=self.db)
        result = agent.define_scope(
            dict(SAMPLE_LEAD, proposal_type="automation"),
            {"project_type": "automation"},
            self.tmp_dir,
        )
        assert result["file_path"]


class TestContractAgent(TestAgentBase):
    def test_verify_contract_no_proposal(self):
        agent = ContractAgent(db=self.db)
        result = agent.verify_contract(SAMPLE_LEAD, None, self.tmp_dir)
        assert result["file_path"]
        assert os.path.isfile(result["file_path"])
        assert result["details"]["agreement_signed"] is False

    def test_verify_contract_with_proposal(self):
        agent = ContractAgent(db=self.db)
        proposal = {"proposal_id": 1, "status": "accepted", "amount": 5000, "proposal_type": "website"}
        result = agent.verify_contract(SAMPLE_LEAD, proposal, self.tmp_dir)
        assert result["details"]["agreement_signed"] is True
        assert result["details"]["deal_amount"] == 5000


class TestPlanningAgent(TestAgentBase):
    def test_create_roadmap(self):
        agent = PlanningAgent(db=self.db)
        result = agent.create_roadmap(SAMPLE_LEAD, {}, self.tmp_dir)
        assert result["file_path"]
        assert os.path.isfile(result["file_path"])
        assert len(result["phases"]) == 5
        with open(result["file_path"]) as f:
            content = f.read()
            assert "Project Roadmap" in content
            assert "Phase 1" in content


class TestHandoverAgent(TestAgentBase):
    def test_prepare_handover(self):
        agent = HandoverAgent(db=self.db)
        result = agent.prepare_handover(SAMPLE_LEAD, {}, self.tmp_dir)
        assert result["file_path"]
        assert os.path.isfile(result["file_path"])
        assert result["destination_department"] == "Website Development Department"

    def test_prepare_handover_automation(self):
        agent = HandoverAgent(db=self.db)
        result = agent.prepare_handover(
            dict(SAMPLE_LEAD, proposal_type="automation"),
            {}, self.tmp_dir,
        )
        assert result["destination_department"] == "AI Automation Department"


class TestCRMAgent(TestAgentBase):
    def test_update_pipeline(self):
        agent = CRMAgent(db=self.db)
        result = agent.update_pipeline("test-001", "Planning")
        assert result["lead_id"] == "test-001"
        assert result["stage"] == "Planning"

    def test_pipeline_stages(self):
        assert len(CRMAgent.PIPELINE_STAGES) == 12
        assert "Onboarding" in CRMAgent.PIPELINE_STAGES
        assert "Completed" in CRMAgent.PIPELINE_STAGES


class TestExecutiveReportAgent(TestAgentBase):
    def test_generate_report(self):
        agent = ExecutiveReportAgent(db=self.db)
        results = {
            "welcome": {"file_path": "/tmp/welcome.md", "email_sent": True},
            "questionnaire": {"file_path": "/tmp/q.md"},
            "requirements": {"file_path": "/tmp/r.md"},
            "assets": {"file_path": "/tmp/a.md"},
            "access": {"file_path": "/tmp/ac.md"},
            "brand": {"file_path": "/tmp/b.md"},
            "scope": {"file_path": "/tmp/s.md"},
            "contract": {"file_path": "/tmp/c.md", "details": {"agreement_signed": True}},
            "roadmap": {"file_path": "/tmp/road.md"},
            "handover": {"file_path": "/tmp/h.md", "destination_department": "Web Dev"},
            "report": {},
        }
        result = agent.generate_report(SAMPLE_LEAD, results, self.tmp_dir)
        assert result["file_path"]
        assert os.path.isfile(result["file_path"])
        with open(result["file_path"]) as f:
            content = f.read()
            assert "Executive Onboarding Report" in content or "EXECUTIVE ONBOARDING REPORT" in content
