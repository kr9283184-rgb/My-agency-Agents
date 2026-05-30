from typing import Optional
from datetime import datetime, timedelta
from client_outreach.agents.base_agent import BaseAgent
from client_outreach.llm.base import LLMProvider


FOLLOW_UP_SEQUENCE = [
    {"step": 1, "day": 1, "channel": "email", "label": "Introduction"},
    {"step": 2, "day": 3, "channel": "email", "label": "Value follow-up"},
    {"step": 3, "day": 7, "channel": "email", "label": "Case study"},
    {"step": 4, "day": 10, "channel": "whatsapp", "label": "WhatsApp check-in"},
    {"step": 5, "day": 14, "channel": "email", "label": "Final follow-up"},
]


class FollowUpAgent(BaseAgent):
    def __init__(self, llm: Optional[LLMProvider] = None, **kwargs):
        super().__init__(**kwargs)
        self.llm = llm

    def schedule_sequence(self, lead_id: str, start_date: Optional[str] = None):
        lead = self.db.get_lead(lead_id)
        if not lead:
            self.log(f"Lead {lead_id} not found")
            return

        base = datetime.now()
        if start_date:
            try:
                base = datetime.fromisoformat(start_date)
            except ValueError:
                pass

        for step in FOLLOW_UP_SEQUENCE:
            scheduled = base + timedelta(days=step["day"])
            body = self._generate_body(lead, step)

            self.db.add_follow_up({
                "lead_id": lead_id,
                "step_number": step["step"],
                "channel": step["channel"],
                "subject": step["label"],
                "body": body,
                "scheduled_at": scheduled.isoformat(),
                "status": "pending",
            })

        self.log(f"Scheduled {len(FOLLOW_UP_SEQUENCE)} follow-ups for {lead.get('company_name', lead_id)}")

    def process_due_follow_ups(self, email_agent=None, whatsapp_agent=None, social_agent=None):
        pending = self.db.get_pending_follow_ups()
        sent_count = 0

        for fu in pending:
            lead = self.db.get_lead(fu["lead_id"])
            if not lead:
                continue

            channel = fu["channel"]
            body = fu["body"]
            comm_id = None

            if channel == "email" and email_agent:
                lead["email"] = lead.get("email", "")
                comm_id = email_agent._send_email(
                    lead, "follow_up", fu.get("subject", ""), lambda l: body
                )
            elif channel == "whatsapp" and whatsapp_agent:
                comm_id = whatsapp_agent._send_message_raw(
                    lead, "follow_up", body
                )
            elif channel in ("linkedin", "facebook", "twitter", "instagram") and social_agent:
                comm_id = social_agent._send_social_message(
                    lead, channel, lambda l: body
                )

            if comm_id:
                self.db.mark_follow_up_sent(fu["sequence_id"])
                sent_count += 1

        self.log(f"Processed {sent_count} due follow-ups")
        return sent_count

    def _generate_body(self, lead: dict, step: dict) -> str:
        if self.llm:
            prompt = (
                f"Write a {step['channel']} message for step {step['step']} "
                f"('{step['label']}') of a sales sequence. "
                f"Lead: {lead.get('contact_name', '')} at {lead.get('company_name', '')}, "
                f"industry: {lead.get('industry', '')}. "
                f"Be helpful and specific. Max 150 words."
            )
            result = self.llm.generate(prompt, temperature=0.7)
            if result.strip():
                return result.strip()

        bodies = {
            1: (
                f"Hi {lead.get('contact_name', 'there')},\n\n"
                f"Reaching out because we help {lead.get('industry', '')} companies "
                f"generate more qualified leads on autopilot."
            ),
            2: (
                f"Hi {lead.get('contact_name', 'there')},\n\n"
                f"Quick follow-up — our clients typically see a 3x increase in "
                f"qualified leads within 30 days. Would you be open to a quick demo?"
            ),
            3: (
                f"Hi {lead.get('contact_name', 'there')},\n\n"
                f"Thought you might find this case study interesting — we helped "
                f"a similar {lead.get('industry', '')} business achieve remarkable results."
            ),
            4: (
                f"Hi {lead.get('contact_name', 'there')}, just checking in! "
                f"Would love to see if we can help you grow."
            ),
            5: (
                f"Hi {lead.get('contact_name', 'there')},\n\n"
                f"Wanted to do one last check-in. If the timing isn't right, "
                f"no worries — I'll leave it with you."
            ),
        }
        return bodies.get(step["step"], "")
