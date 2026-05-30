from typing import Optional
from datetime import datetime

from client_outreach.agents.base_agent import BaseAgent
from client_outreach.llm.base import LLMProvider
from client_outreach.compliance.rate_limiter import RateLimiter
from client_outreach.compliance.consent_manager import ConsentManager
from client_outreach.compliance.footer_generator import FooterGenerator
from client_outreach.email.smtp_sender import SMTPSender


class EmailOutreachAgent(BaseAgent):
    def __init__(
        self,
        llm: Optional[LLMProvider] = None,
        rate_limiter: Optional[RateLimiter] = None,
        consent_manager: Optional[ConsentManager] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.llm = llm
        self.rate_limiter = rate_limiter or RateLimiter()
        self.consent = consent_manager or ConsentManager()
        self.footer = FooterGenerator()
        self.sender = SMTPSender()

    def send_introduction(self, lead: dict) -> Optional[int]:
        return self._send_email(
            lead=lead,
            email_type="introduction",
            subject_template=f"Helping {lead.get('company_name', 'your company')} grow",
            body_fn=self._generate_intro_body,
        )

    def send_follow_up(self, lead: dict, step: int = 1) -> Optional[int]:
        subjects = {
            1: f"Quick thought for {lead.get('company_name', 'your team')}",
            2: f"Case study: results we've delivered",
            3: f"Still interested?",
        }
        subject = subjects.get(
            step, f"Following up ({datetime.now().strftime('%b %d')})"
        )
        return self._send_email(
            lead=lead,
            email_type="follow_up",
            subject_template=subject,
            body_fn=lambda l: self._generate_follow_up_body(l, step),
        )

    def send_proposal(self, lead: dict, proposal_title: str = "Proposal") -> Optional[int]:
        return self._send_email(
            lead=lead,
            email_type="proposal",
            subject_template=f"Proposal: {proposal_title} for {lead.get('company_name', 'your company')}",
            body_fn=self._generate_proposal_body,
        )

    def send_meeting_request(self, lead: dict) -> Optional[int]:
        return self._send_email(
            lead=lead,
            email_type="meeting_request",
            subject_template=f"Meeting request — {lead.get('company_name', 'your company')}",
            body_fn=self._generate_meeting_body,
        )

    def send_re_engagement(self, lead: dict) -> Optional[int]:
        return self._send_email(
            lead=lead,
            email_type="re_engagement",
            subject_template=f"Still there, {lead.get('contact_name', 'there')}?",
            body_fn=self._generate_re_engagement_body,
        )

    def _send_email(
        self,
        lead: dict,
        email_type: str,
        subject_template: str,
        body_fn,
    ) -> Optional[int]:
        lead_id = lead.get("lead_id", "")
        email = lead.get("email", "")

        if not email:
            self.log(f"No email for lead {lead_id}")
            return None

        if not self.consent.require_consent(lead_id, "email"):
            self.log(f"No email consent for lead {lead_id}")
            return None

        self.rate_limiter.wait_if_needed("email")

        body = body_fn(lead) + self.footer.email_footer()
        success = self.sender.send(to=email, subject=subject_template, body=body)

        if success:
            comm_id = self.db.add_communication({
                "lead_id": lead_id,
                "channel": "email",
                "direction": "outbound",
                "subject": subject_template,
                "body": body,
                "status": "sent",
            })
            self.rate_limiter.record_send("email")
            self.db.update_pipeline_stage(lead_id, "Contacted")
            self.log(f"Sent {email_type} email to {email}")
            return comm_id
        return None

    def _generate_intro_body(self, lead: dict) -> str:
        if self.llm:
            prompt = (
                f"Write a friendly, personalized sales introduction email (3-4 paragraphs) "
                f"to {lead.get('contact_name', 'the owner')} at {lead.get('company_name', '')}, "
                f"a {lead.get('industry', '')} company in {lead.get('location', '')}. "
                f"Offer AI-powered lead generation services. "
                f"Be professional, specific, and conversational. "
                f"Do NOT use generic sales language."
            )
            result = self.llm.generate(prompt, temperature=0.7)
            if result.strip():
                return result.strip()
        return (
            f"Hi {lead.get('contact_name', 'there')},\n\n"
            f"I noticed {lead.get('company_name', 'your company')} is in the "
            f"{lead.get('industry', '')} space. We've been helping similar businesses "
            f"generate more qualified leads through AI-powered outreach.\n\n"
            f"Would you be open to a brief chat about how we could help you grow your pipeline?"
        )

    def _generate_follow_up_body(self, lead: dict, step: int) -> str:
        if self.llm:
            prompt = (
                f"Write a brief follow-up email to {lead.get('contact_name', 'the owner')} "
                f"at {lead.get('company_name', '')}. This is follow-up #{step}. "
                f"Be helpful, not pushy. Reference previous message. "
                f"Keep it to 2-3 short paragraphs."
            )
            result = self.llm.generate(prompt, temperature=0.7)
            if result.strip():
                return result.strip()
        return (
            f"Hi {lead.get('contact_name', 'there')},\n\n"
            f"Just following up on my previous message. We've helped "
            f"several {lead.get('industry', '')} businesses achieve great results "
            f"with our outreach system.\n\n"
            f"Would you have 15 minutes this week to discuss?"
        )

    def _generate_proposal_body(self, lead: dict) -> str:
        return (
            f"Hi {lead.get('contact_name', 'there')},\n\n"
            f"As promised, here's our proposal for {lead.get('company_name', 'your company')}. "
            f"We've tailored it based on our conversation and believe it addresses "
            f"your key priorities.\n\n"
            f"Please review at your convenience, and let me know if you have any questions."
        )

    def _generate_meeting_body(self, lead: dict) -> str:
        return (
            f"Hi {lead.get('contact_name', 'there')},\n\n"
            f"Would you be available for a 20-minute call this week? "
            f"I'd love to show you how we can help {lead.get('company_name', 'your company')} "
            f"generate more qualified leads.\n\n"
            f"Please let me know what time works best for you."
        )

    def _generate_re_engagement_body(self, lead: dict) -> str:
        return (
            f"Hi {lead.get('contact_name', 'there')},\n\n"
            f"It's been a while since we last connected. I wanted to check in "
            f"and see if your priorities have shifted.\n\n"
            f"If now isn't the right time, no worries at all — just let me know."
        )
