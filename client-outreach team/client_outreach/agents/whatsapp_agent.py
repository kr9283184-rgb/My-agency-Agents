from typing import Optional
from client_outreach.agents.base_agent import BaseAgent
from client_outreach.llm.base import LLMProvider
from client_outreach.compliance.rate_limiter import RateLimiter
from client_outreach.compliance.consent_manager import ConsentManager
from client_outreach.compliance.footer_generator import FooterGenerator


class WhatsAppCommunicationAgent(BaseAgent):
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

    def send_first_contact(self, lead: dict) -> Optional[int]:
        return self._send_message(lead, "first_contact", self._generate_first_message)

    def send_follow_up(self, lead: dict) -> Optional[int]:
        return self._send_message(lead, "follow_up", self._generate_follow_up)

    def send_appointment_reminder(self, lead: dict, appointment_time: str) -> Optional[int]:
        body = (
            f"Hi {lead.get('contact_name', 'there')}, just a quick reminder "
            f"about our call scheduled for {appointment_time}. "
            f"Looking forward to speaking with you!"
        )
        return self._send_message_raw(lead, "appointment_reminder", body)

    def send_proposal_link(self, lead: dict, proposal_url: str) -> Optional[int]:
        body = (
            f"Hi {lead.get('contact_name', 'there')}, here's the proposal "
            f"we discussed: {proposal_url}. Let me know if you have any questions!"
        )
        return self._send_message_raw(lead, "proposal", body)

    def send_support_message(self, lead: dict, message: str) -> Optional[int]:
        return self._send_message_raw(lead, "support", message)

    def _send_message(self, lead: dict, msg_type: str, body_fn) -> Optional[int]:
        body = body_fn(lead) + self.footer.whatsapp_footer()
        return self._send_message_raw(lead, msg_type, body)

    def _send_message_raw(self, lead: dict, msg_type: str, body: str) -> Optional[int]:
        lead_id = lead.get("lead_id", "")
        phone = lead.get("whatsapp_phone", "")

        if not phone:
            self.log(f"No WhatsApp number for lead {lead_id}")
            return None

        if not self.consent.require_consent(lead_id, "whatsapp"):
            self.log(f"No WhatsApp consent for lead {lead_id}")
            return None

        self.rate_limiter.wait_if_needed("whatsapp")

        self.log(f"[SIMULATED] WhatsApp {msg_type} to {phone}: {body[:100]}...")
        comm_id = self.db.add_communication({
            "lead_id": lead_id,
            "channel": "whatsapp",
            "direction": "outbound",
            "subject": msg_type,
            "body": body,
            "status": "sent",
        })
        self.rate_limiter.record_send("whatsapp")
        self.db.update_pipeline_stage(lead_id, "Contacted")
        self.log(f"Sent WhatsApp {msg_type} to {phone}")
        return comm_id

    def _generate_first_message(self, lead: dict) -> str:
        if self.llm:
            prompt = (
                f"Write a professional, human-like WhatsApp first-contact message "
                f"to {lead.get('contact_name', 'the owner')} at {lead.get('company_name', '')}. "
                f"Be friendly, concise, and personalized. Max 200 words."
            )
            result = self.llm.generate(prompt, temperature=0.7)
            if result.strip():
                return result.strip()
        return (
            f"Hi {lead.get('contact_name', 'there')}! This is from {lead.get('company_name', '')}."
        )

    def _generate_follow_up(self, lead: dict) -> str:
        return (
            f"Hi {lead.get('contact_name', 'there')}, following up on my previous message. "
            f"Would love to connect and discuss how we can help."
        )
