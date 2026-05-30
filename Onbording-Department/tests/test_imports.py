def test_import_onboarding_department():
    import onboarding_department
    assert hasattr(onboarding_department, "OnboardingOrchestrator")
    assert hasattr(onboarding_department, "OnboardingResult")
    assert hasattr(onboarding_department, "OnboardingDatabase")


def test_import_config():
    from onboarding_department.config import Config
    assert hasattr(Config, "SMTP_HOST")


def test_import_database():
    from onboarding_department.database import OnboardingDatabase
    assert hasattr(OnboardingDatabase, "add_lead")


def test_import_base_agent():
    from onboarding_department.agents.base_agent import BaseAgent
    assert hasattr(BaseAgent, "log")


def test_import_all_agents():
    from onboarding_department.agents.client_manager_agent import ClientManagerAgent
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

    assert ClientManagerAgent is not None
    assert WelcomeAgent is not None
    assert RequirementAgent is not None


def test_import_email():
    from onboarding_department.email.smtp_sender import SMTPSender
    from onboarding_department.email.templates import WELCOME_EMAIL_TEMPLATE
    assert hasattr(SMTPSender, "send")
    assert "Welcome" in WELCOME_EMAIL_TEMPLATE


def test_import_browser():
    from onboarding_department.browser.whatsapp import WhatsAppAutomation
    assert hasattr(WhatsAppAutomation, "send_message")


def test_import_orchestrator():
    from onboarding_department.orchestrator import OnboardingOrchestrator, OnboardingResult
    assert hasattr(OnboardingOrchestrator, "run")


def test_import_cli():
    from onboarding_department.cli import main
    assert callable(main)
