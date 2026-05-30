def test_imports():
    from client_outreach.config import Config
    from client_outreach.database import OutreachDatabase
    from client_outreach.orchestrator import Orchestrator, OutreachResult
    from client_outreach.llm.base import LLMProvider
    from client_outreach.llm.ollama_provider import OllamaProvider
    from client_outreach.agents.base_agent import BaseAgent
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
    from client_outreach.compliance.footer_generator import FooterGenerator
    from client_outreach.email.smtp_sender import SMTPSender
    from client_outreach.calendar.caldav_calendar import CalDAVCalendar
    assert True
