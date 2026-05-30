import os
from typing import Optional
from datetime import datetime
from dataclasses import dataclass, field

from client_outreach.config import Config
from client_outreach.database import OutreachDatabase as SQLiteDB
from client_outreach.llm.ollama_provider import OllamaProvider
from client_outreach.llm.base import LLMProvider

from client_outreach.agents.crm_agent import CRMAgent
from client_outreach.agents.lead_intelligence import LeadIntelligenceAgent
from client_outreach.agents.email_outreach import EmailOutreachAgent
from client_outreach.agents.whatsapp_agent import WhatsAppCommunicationAgent
from client_outreach.agents.social_media_agent import SocialMediaOutreachAgent
from client_outreach.agents.conversation_analysis import ConversationAnalysisAgent
from client_outreach.agents.follow_up import FollowUpAgent
from client_outreach.agents.appointment_booking import AppointmentBookingAgent
from client_outreach.agents.proposal_generation import ProposalGenerationAgent
from client_outreach.agents.executive_report import ExecutiveReportingAgent

from client_outreach.compliance.rate_limiter import RateLimiter
from client_outreach.compliance.consent_manager import ConsentManager


@dataclass
class OutreachResult:
    db: object = None
    leads_imported: int = 0
    emails_sent: int = 0
    messages_sent: int = 0
    meetings_booked: int = 0
    proposals_generated: int = 0
    replies_analyzed: int = 0
    follow_ups_scheduled: int = 0
    report_path: str = ""
    daily_report: str = ""
    weekly_report: str = ""

    def summary(self) -> dict:
        return {
            "leads_imported": self.leads_imported,
            "emails_sent": self.emails_sent,
            "messages_sent": self.messages_sent,
            "meetings_booked": self.meetings_booked,
            "proposals_generated": self.proposals_generated,
            "replies_analyzed": self.replies_analyzed,
            "follow_ups_scheduled": self.follow_ups_scheduled,
            "report_path": self.report_path,
        }


class Orchestrator:
    def __init__(
        self,
        db: Optional[SQLiteDB] = None,
        llm: Optional[LLMProvider] = None,
        output_dir: Optional[str] = None,
    ):
        self.output_dir = output_dir or Config.OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

        self._db = db or SQLiteDB(db_path=os.path.join(self.output_dir, "outreach.db"))
        self.llm = llm or self._auto_select_llm()

        self.rate_limiter = RateLimiter()
        self.consent_manager = ConsentManager(db=self._db)

        self.crm = CRMAgent(db=self._db)
        self.lead_intel = LeadIntelligenceAgent(llm=self.llm, db=self._db)
        self.email = EmailOutreachAgent(
            llm=self.llm, rate_limiter=self.rate_limiter,
            consent_manager=self.consent_manager, db=self._db,
        )
        self.whatsapp = WhatsAppCommunicationAgent(
            llm=self.llm, rate_limiter=self.rate_limiter,
            consent_manager=self.consent_manager, db=self._db,
        )
        self.social = SocialMediaOutreachAgent(
            llm=self.llm, rate_limiter=self.rate_limiter,
            consent_manager=self.consent_manager, db=self._db,
        )
        self.conversation = ConversationAnalysisAgent(llm=self.llm, db=self._db)
        self.follow_up = FollowUpAgent(llm=self.llm, db=self._db)
        self.booking = AppointmentBookingAgent(db=self._db)
        self.proposals = ProposalGenerationAgent(llm=self.llm, output_dir=self.output_dir, db=self._db)
        self.reporting = ExecutiveReportingAgent(llm=self.llm, db=self._db)

    def _auto_select_llm(self) -> Optional[LLMProvider]:
        ollama = OllamaProvider()
        try:
            if ollama.is_available():
                print(f"[Orchestrator] Using LLM: Ollama ({ollama.model})")
                return ollama
        except Exception:
            pass
        print("[Orchestrator] No LLM available — using rule-based fallbacks")
        return None

    def run(self, leads: list[dict]) -> OutreachResult:
        result = OutreachResult(db=self._db)

        print(f"\n{'='*60}")
        print(f"  AI SALES & OUTREACH DEPARTMENT")
        print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"{'='*60}\n")

        # Step 1: Import leads into CRM
        print("\n[Step 1/8] CRM — Importing Leads")
        self.crm.import_leads(leads)
        result.leads_imported = len(leads)

        # Step 2: Lead Intelligence
        print("\n[Step 2/8] Lead Intelligence — Researching Leads")
        for lead in leads:
            self.lead_intel.research_lead(lead)
        self.log("Researched all leads")

        # Step 3: Initial Outreach (Email + WhatsApp + Social)
        print("\n[Step 3/8] Initial Outreach — Contacting Leads")
        for lead in leads:
            lead_id = lead.get("lead_id", "")
            company = lead.get("company_name", "")

            consent = self.consent_manager.get_consent_summary(lead_id)

            if lead.get("email") and consent.get("email"):
                cid = self.email.send_introduction(lead)
                if cid:
                    result.emails_sent += 1

            if lead.get("whatsapp_phone") and consent.get("whatsapp"):
                cid = self.whatsapp.send_first_contact(lead)
                if cid:
                    result.messages_sent += 1

            for ch in ["linkedin", "facebook", "twitter", "instagram"]:
                if consent.get(ch):
                    if ch == "linkedin" and lead.get("linkedin_url"):
                        cid = self.social.send_linkedin_connection(lead)
                        if cid:
                            result.messages_sent += 1
                    elif ch == "facebook" and lead.get("facebook_url"):
                        cid = self.social.send_facebook_message(lead)
                        if cid:
                            result.messages_sent += 1
                    elif ch == "twitter" and lead.get("twitter_url"):
                        cid = self.social.send_twitter_dm(lead)
                        if cid:
                            result.messages_sent += 1

        # Schedule follow-up sequences
        print("\n[Step 4/8] Follow-Up — Scheduling Sequences")
        for lead in leads:
            self.follow_up.schedule_sequence(lead.get("lead_id", ""))
            result.follow_ups_scheduled += 1

        # Step 5: Process any due follow-ups
        print("\n[Step 5/8] Follow-Up — Processing Due Messages")
        sent = self.follow_up.process_due_follow_ups(
            email_agent=self.email,
            whatsapp_agent=self.whatsapp,
            social_agent=self.social,
        )

        # Step 6: Conversation Analysis (simulate analyzing any inbound)
        print("\n[Step 6/8] Conversation Analysis — Analyzing Responses")
        for lead in leads:
            comms = self._db.get_communications(lead.get("lead_id", ""))
            for comm in comms:
                if comm["direction"] == "inbound" and comm.get("body"):
                    analysis = self.conversation.analyze_response(
                        lead.get("lead_id", ""),
                        comm["body"],
                        comm["comm_id"],
                    )
                    result.replies_analyzed += 1

        # Step 7: Appointments & Proposals
        print("\n[Step 7/8] Appointments & Proposals")
        for lead in leads:
            analysis_list = self._db.get_analyses(lead.get("lead_id", ""))
            if analysis_list:
                classification = analysis_list[0].get("classification", "")
                if classification in ("Hot Lead", "Warm Lead"):
                    apt_id = self.booking.propose_slots(lead)
                    if apt_id:
                        result.meetings_booked += 1

                    fp = self.proposals.send_proposal(lead)
                    if fp:
                        result.proposals_generated += 1

        # Step 8: Generate Reports
        print("\n[Step 8/8] Executive Reports")
        print()
        result.daily_report = self.reporting.generate_daily_report()
        print()
        result.weekly_report = self.reporting.generate_weekly_report()

        print(f"\n{'='*60}")
        s = result.summary()
        for k, v in s.items():
            print(f"  {k.replace('_', ' ').title()}: {v}")
        print(f"{'='*60}\n")

        return result

    def import_leads_only(self, leads: list[dict]) -> int:
        self.crm.import_leads(leads)
        return len(leads)

    def research_only(self, leads: list[dict]) -> list[dict]:
        for lead in leads:
            self.lead_intel.research_lead(lead)
        return leads

    def send_outreach_only(self, leads: list[dict]) -> dict:
        stats = {"email": 0, "whatsapp": 0, "social": 0}
        for lead in leads:
            lead_id = lead.get("lead_id", "")
            consent = self.consent_manager.get_consent_summary(lead_id)
            if lead.get("email") and consent.get("email"):
                if self.email.send_introduction(lead):
                    stats["email"] += 1
            if lead.get("whatsapp_phone") and consent.get("whatsapp"):
                if self.whatsapp.send_first_contact(lead):
                    stats["whatsapp"] += 1
        return stats

    def log(self, msg: str):
        print(f"[Orchestrator] {msg}")
