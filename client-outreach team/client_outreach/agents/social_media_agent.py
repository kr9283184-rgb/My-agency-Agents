from typing import Optional
from client_outreach.agents.base_agent import BaseAgent
from client_outreach.llm.base import LLMProvider
from client_outreach.compliance.rate_limiter import RateLimiter
from client_outreach.compliance.consent_manager import ConsentManager
from client_outreach.compliance.footer_generator import FooterGenerator


class SocialMediaOutreachAgent(BaseAgent):
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

    def send_linkedin_connection(self, lead: dict) -> Optional[int]:
        lead_id = lead.get("lead_id", "")
        url = lead.get("linkedin_url", "")
        if not url:
            self.log(f"No LinkedIn URL for lead {lead_id}")
            return None
        if not self.consent.require_consent(lead_id, "linkedin"):
            self.log(f"No LinkedIn consent for lead {lead_id}")
            return None
        self.rate_limiter.wait_if_needed("linkedin")

        note = self._generate_linkedin_note(lead)
        self.log(f"[SIMULATED] LinkedIn connection request to {url}: {note}")
        comm_id = self.db.add_communication({
            "lead_id": lead_id,
            "channel": "linkedin",
            "direction": "outbound",
            "subject": "connection_request",
            "body": note,
            "status": "sent",
        })
        self.rate_limiter.record_send("linkedin")
        self.db.update_pipeline_stage(lead_id, "Contacted")
        self.log(f"LinkedIn connection sent to {lead.get('company_name', '')}")
        return comm_id

    def send_linkedin_message(self, lead: dict) -> Optional[int]:
        return self._send_social_message(lead, "linkedin", self._generate_linkedin_message)

    def send_facebook_message(self, lead: dict) -> Optional[int]:
        return self._send_social_message(lead, "facebook", self._generate_social_message)

    def send_twitter_dm(self, lead: dict) -> Optional[int]:
        return self._send_social_message(lead, "twitter", self._generate_social_message)

    def send_instagram_dm(self, lead: dict) -> Optional[int]:
        return self._send_social_message(lead, "instagram", self._generate_social_message)

    def _send_social_message(
        self, lead: dict, channel: str, body_fn
    ) -> Optional[int]:
        lead_id = lead.get("lead_id", "")
        if not self.consent.require_consent(lead_id, channel):
            self.log(f"No {channel} consent for lead {lead_id}")
            return None
        self.rate_limiter.wait_if_needed(channel)

        body = body_fn(lead) + self.footer.social_footer()
        self.log(f"[SIMULATED] {channel} DM to {lead.get('contact_name', '')}: {body[:100]}...")
        comm_id = self.db.add_communication({
            "lead_id": lead_id,
            "channel": channel,
            "direction": "outbound",
            "subject": "direct_message",
            "body": body,
            "status": "sent",
        })
        self.rate_limiter.record_send(channel)
        self.db.update_pipeline_stage(lead_id, "Contacted")
        self.log(f"Sent {channel} DM to {lead.get('company_name', '')}")
        return comm_id

    def _generate_linkedin_note(self, lead: dict) -> str:
        return (
            f"Hi {lead.get('contact_name', 'there')}, I've been following "
            f"{lead.get('company_name', 'your company')}'s work and thought "
            f"it would be great to connect!"
        )

    def _generate_linkedin_message(self, lead: dict) -> str:
        return (
            f"Thanks for connecting, {lead.get('contact_name', 'there')}! "
            f"I help {lead.get('industry', '')} businesses generate more leads "
            f"through AI-powered outreach. Would you be open to a quick chat?"
        )

    def _generate_social_message(self, lead: dict) -> str:
        return (
            f"Hi {lead.get('contact_name', 'there')}! Love what "
            f"{lead.get('company_name', 'your company')} is doing. "
            f"Would you be interested in learning how we help businesses "
            f"like yours grow their pipeline?"
        )

    def send_follow_up(self, lead: dict, channel: str = "linkedin") -> Optional[int]:
        if channel == "linkedin":
            return self.send_linkedin_message(lead)
        return self._send_social_message(lead, channel, self._generate_follow_up_body)

    def _generate_follow_up_body(self, lead: dict) -> str:
        return (
            f"Hi {lead.get('contact_name', 'there')}, just following up on my previous message. "
            f"Would love to connect and explore how we might help."
        )
