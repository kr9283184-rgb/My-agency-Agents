from typing import Optional
from onboarding_department.agents.base_agent import BaseAgent
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


class ClientManagerAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.welcome_agent = WelcomeAgent(db=self.db)
        self.requirement_agent = RequirementAgent(db=self.db)
        self.questionnaire_agent = QuestionnaireAgent(db=self.db)
        self.asset_agent = AssetAgent(db=self.db)
        self.access_agent = AccessAgent(db=self.db)
        self.brand_agent = BrandAgent(db=self.db)
        self.scope_agent = ScopeAgent(db=self.db)
        self.contract_agent = ContractAgent(db=self.db)
        self.planning_agent = PlanningAgent(db=self.db)
        self.handover_agent = HandoverAgent(db=self.db)
        self.crm_agent = CRMAgent(db=self.db)
        self.executive_report_agent = ExecutiveReportAgent(db=self.db)

    def onboard_lead(self, lead: dict, proposal: Optional[dict] = None, output_dir: str = "") -> dict:
        company = lead.get("company_name", "Unknown")
        lead_id = lead.get("lead_id", "")
        self.log(f"Starting onboarding for {company} ({lead_id})")

        self.db.add_lead({
            "lead_id": lead_id,
            "company_name": company,
            "contact_name": lead.get("contact_name", ""),
            "email": lead.get("email", ""),
            "whatsapp_phone": lead.get("whatsapp_phone", ""),
            "industry": lead.get("industry", ""),
            "proposal_type": proposal.get("proposal_type", "") if proposal else "",
            "deal_amount": proposal.get("amount", 0.0) if proposal else 0.0,
        })

        results = {}

        welcome = self.welcome_agent.send_welcome_package(lead, output_dir)
        results["welcome"] = welcome
        if welcome.get("status") == "sent":
            self.db.update_status(lead_id, "welcome_sent", "welcome")

        questionnaire = self.questionnaire_agent.generate_questionnaire(lead, output_dir)
        results["questionnaire"] = questionnaire
        self.db.update_status(lead_id, "questionnaire_sent", "questionnaire")
        self.db.add_output(lead_id, "questionnaire", questionnaire.get("file_path", ""))

        requirements = self.requirement_agent.collect_requirements(lead, proposal, output_dir)
        results["requirements"] = requirements
        self.db.update_status(lead_id, "requirements_collected", "requirements")
        self.db.add_output(lead_id, "requirements", requirements.get("file_path", ""))

        assets = self.asset_agent.collect_assets(lead, output_dir)
        results["assets"] = assets
        self.db.update_status(lead_id, "assets_requested", "assets")
        self.db.add_output(lead_id, "assets", assets.get("file_path", ""))

        access = self.access_agent.track_access(lead, output_dir)
        results["access"] = access
        self.db.update_status(lead_id, "access_checklist_created", "access")
        self.db.add_output(lead_id, "access", access.get("file_path", ""))

        brand = self.brand_agent.analyze_brand(lead, output_dir)
        results["brand"] = brand
        self.db.update_status(lead_id, "brand_analysis_done", "brand")
        self.db.add_output(lead_id, "brand", brand.get("file_path", ""))

        scope = self.scope_agent.define_scope(lead, requirements.get("details", {}), output_dir)
        results["scope"] = scope
        self.db.update_status(lead_id, "scope_defined", "scope")
        self.db.add_output(lead_id, "scope", scope.get("file_path", ""))

        contract = self.contract_agent.verify_contract(lead, proposal, output_dir)
        results["contract"] = contract
        self.db.update_status(lead_id, "contract_verified", "contract")
        self.db.add_output(lead_id, "contract", contract.get("file_path", ""))

        roadmap = self.planning_agent.create_roadmap(lead, scope.get("details", {}), output_dir)
        results["roadmap"] = roadmap
        self.db.update_status(lead_id, "roadmap_created", "roadmap")
        self.db.add_output(lead_id, "roadmap", roadmap.get("file_path", ""))

        handover = self.handover_agent.prepare_handover(lead, results, output_dir)
        results["handover"] = handover
        self.db.update_status(lead_id, "handover_completed", "handover")
        self.db.add_output(lead_id, "handover", handover.get("file_path", ""))

        crm = self.crm_agent.update_pipeline(lead_id, "Planning")
        results["crm"] = crm
        self.db.update_status(lead_id, "crm_updated", "crm")

        report = self.executive_report_agent.generate_report(lead, results, output_dir)
        results["report"] = report
        self.db.update_status(lead_id, "report_generated", "report")
        self.db.add_output(lead_id, "report", report.get("file_path", ""))

        self.db.update_status(lead_id, "completed")
        self.log(f"Onboarding completed for {company}")

        return results
