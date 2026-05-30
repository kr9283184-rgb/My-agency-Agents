import os
from typing import Optional
from datetime import datetime
from dataclasses import dataclass, field

from lead_gen_master.config import Config
from lead_gen_master.memory.memory_manager import MemoryManager
from lead_gen_master.memory.schemas import Lead as LeadSchema

from lead_gen_master.llm.groq_provider import GroqProvider
from lead_gen_master.llm.openai_provider import OpenAIProvider
from lead_gen_master.llm.ollama_provider import OllamaProvider
from lead_gen_master.llm.base import LLMProvider

from lead_gen_master.agents.market_intelligence import (
    MarketIntelligenceAgent,
)
from lead_gen_master.agents.google_business_research import (
    GoogleBusinessResearchAgent,
)
from lead_gen_master.agents.linkedin_research import (
    LinkedInResearchAgent,
)
from lead_gen_master.agents.social_media_research import (
    SocialMediaResearchAgent,
)
from lead_gen_master.agents.website_audit import (
    WebsiteAuditAgent,
)
from lead_gen_master.agents.lead_qualification import (
    LeadQualificationAgent,
)
from lead_gen_master.agents.duplicate_detection import (
    DuplicateDetectionAgent,
)
from lead_gen_master.agents.crm_management import (
    CRMManagementAgent,
)
from lead_gen_master.agents.sales_intelligence import (
    SalesIntelligenceAgent,
)
from lead_gen_master.agents.excel_reporting import (
    ExcelReportingAgent,
)
from lead_gen_master.agents.executive_report import (
    ExecutiveReportAgent,
)


@dataclass
class LeadDatabase:
    leads: list[dict] = field(default_factory=list)
    audits: list[dict] = field(default_factory=list)
    briefs: list[dict] = field(default_factory=list)
    industry_insights: list[dict] = field(default_factory=list)
    report_path: str = ""
    executive_report: str = ""

    @property
    def qualified_leads(self) -> list[dict]:
        return [
            l for l in self.leads if l.get("lead_score", 0) >= 50
        ]

    @property
    def high_priority_leads(self) -> list[dict]:
        return [
            l for l in self.leads if l.get("priority") == "High"
        ]

    def summary(self) -> dict:
        return {
            "total_leads": len(self.leads),
            "qualified_leads": len(self.qualified_leads),
            "high_priority": len(self.high_priority_leads),
            "audits": len(self.audits),
            "briefs": len(self.briefs),
            "report_path": self.report_path,
        }


class Orchestrator:
    def __init__(
        self,
        target_industry: Optional[str] = None,
        target_location: Optional[str] = None,
        max_leads: int = 25,
        output_dir: Optional[str] = None,
        llm: Optional[LLMProvider] = None,
    ):
        self.target_industry = (
            target_industry or Config.DEFAULT_INDUSTRY
        )
        self.target_location = (
            target_location or Config.DEFAULT_LOCATION
        )
        self.max_leads = max_leads
        self.output_dir = output_dir or Config.OUTPUT_DIR

        os.makedirs(self.output_dir, exist_ok=True)

        self.memory = MemoryManager(output_dir=self.output_dir)

        self.llm = llm or self._auto_select_llm()

        self.market_intel = MarketIntelligenceAgent(
            llm=self.llm, memory=self.memory
        )
        self.business_research = GoogleBusinessResearchAgent(
            llm=self.llm, memory=self.memory
        )
        self.linkedin = LinkedInResearchAgent(
            llm=self.llm, memory=self.memory
        )
        self.social = SocialMediaResearchAgent(
            memory=self.memory
        )
        self.website_audit = WebsiteAuditAgent(
            llm=self.llm, memory=self.memory
        )
        self.qualification = LeadQualificationAgent(
            llm=self.llm, memory=self.memory
        )
        self.dedup = DuplicateDetectionAgent(
            memory=self.memory
        )
        self.crm = CRMManagementAgent(
            memory=self.memory
        )
        self.sales = SalesIntelligenceAgent(
            llm=self.llm, memory=self.memory
        )
        self.excel = ExcelReportingAgent(
            memory=self.memory
        )
        self.exec_report = ExecutiveReportAgent(
            llm=self.llm, memory=self.memory
        )

    def _auto_select_llm(self) -> Optional[LLMProvider]:
        providers = []

        groq = GroqProvider()
        if groq.is_available():
            providers.append(groq)

        oai = OpenAIProvider()
        if oai.is_available():
            providers.append(oai)

        ollama = OllamaProvider()
        try:
            if ollama.is_available():
                providers.append(ollama)
        except Exception:
            pass

        if providers:
            print(
                f"[Orchestrator] Using LLM: {type(providers[0]).__name__}"
            )
            return providers[0]

        print(
            "[Orchestrator] No LLM available — "
            "using rule-based fallbacks"
        )
        return None

    def run(self) -> LeadDatabase:
        print(f"\n{'='*60}")
        print(
            f"  AI LEAD GENERATION MASTER — "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        print(
            f"  Target: {self.target_industry} @ "
            f"{self.target_location}"
        )
        print(f"{'='*60}\n")

        # Step 1: Market Intelligence
        print("\n[Step 1/7] Market Intelligence")
        industry = self.market_intel.analyze_industry(
            self.target_industry, self.target_location
        )

        # Step 2: Business Discovery
        print("\n[Step 2/7] Business Discovery")
        leads = self.business_research.find_businesses(
            self.target_industry,
            self.target_location,
            self.max_leads,
        )

        if not leads:
            print("  No leads found. Aborting.")
            return LeadDatabase()

        # Step 3: LinkedIn Enrichment
        print("\n[Step 3/7] LinkedIn Research")
        leads = self.linkedin.enrich_leads(leads)

        # Step 4: Social Presence
        print("\n[Step 4/7] Social Media Research")
        leads = self.social.enrich_leads(leads)

        # Step 5: Website Audit
        print("\n[Step 5/7] Website Audit")
        audits = self.website_audit.audit_leads(leads)

        # Step 6: Qualification
        print("\n[Step 6/7] Lead Qualification")
        leads = self.qualification.qualify_leads(leads, audits)

        # Deduplicate
        leads = self.dedup.deduplicate(leads)

        # Structure CRM records
        leads = self.crm.structure_records(leads)

        # Step 7: Sales Briefs + Report
        print("\n[Step 7/7] Reporting")
        briefs = self.sales.generate_briefs(leads)

        report_path = self.excel.generate_report(leads, audits)
        exec_report_text = self.exec_report.generate(
            leads, audits, briefs
        )

        print(f"\n{'='*60}")
        print(f"  REPORT GENERATED: {report_path}")
        print(f"{'='*60}\n")

        print(exec_report_text)

        return LeadDatabase(
            leads=leads,
            audits=audits,
            briefs=briefs,
            industry_insights=[industry],
            report_path=report_path,
            executive_report=exec_report_text,
        )

    def run_market_intel_only(self) -> dict:
        return self.market_intel.analyze_industry(
            self.target_industry, self.target_location
        )

    def run_research_only(self) -> list[dict]:
        return self.business_research.find_businesses(
            self.target_industry,
            self.target_location,
            self.max_leads,
        )
