from typing import Optional
from lead_gen_master.agents.base_agent import BaseAgent
from lead_gen_master.llm.base import LLMProvider

SERVICES = [
    "Website Design & Development",
    "AI Automation Solutions",
    "AI Chatbots",
    "Business Process Automation",
    "SEO Services",
    "Digital Marketing",
    "Branding",
    "Custom Software Development",
]


class LeadQualificationAgent(BaseAgent):
    def __init__(
        self,
        llm: Optional[LLMProvider] = None,
        memory=None,
    ):
        super().__init__(memory)
        self.llm = llm

    def qualify(self, lead: dict, audit: Optional[dict] = None) -> dict:
        self.log(f"Qualifying lead: {lead.get('company_name', '')}")

        score = self._calculate_score(lead, audit)
        priority = self._determine_priority(score)
        service = self._recommend_service(lead, score)

        lead["lead_score"] = score
        lead["priority"] = priority
        lead["recommended_service"] = service
        return lead

    def qualify_leads(
        self,
        leads: list[dict],
        audits: Optional[list[dict]] = None,
    ) -> list[dict]:
        self.log(f"Qualifying {len(leads)} leads")

        audit_map = {}
        if audits:
            audit_map = {a.get("lead_id", ""): a for a in audits}

        if self.llm and self.llm.is_available():
            return self._llm_qualify(leads, audit_map)
        return self._rule_qualify(leads, audit_map)

    def _llm_qualify(
        self,
        leads: list[dict],
        audit_map: dict,
    ) -> list[dict]:
        qualified = []
        for lead in leads:
            audit = audit_map.get(lead.get("lead_id", ""))
            prompt = self._build_llm_prompt(lead, audit)
            result = self.llm.generate_json(prompt)
            try:
                import json
                import re

                cleaned = re.sub(
                    r"^```(?:json)?\s*|\s*```$",
                    "",
                    result,
                    flags=re.DOTALL,
                )
                data = json.loads(cleaned)
                lead["lead_score"] = data.get("lead_score", 50)
                lead["priority"] = data.get("priority", "Medium")
                lead["recommended_service"] = data.get(
                    "recommended_service", SERVICES[0]
                )
            except (json.JSONDecodeError, AttributeError):
                lead = self._rule_qualify_single(lead, audit)
            qualified.append(lead)
        return qualified

    def _rule_qualify(
        self,
        leads: list[dict],
        audit_map: dict,
    ) -> list[dict]:
        return [
            self._rule_qualify_single(
                lead, audit_map.get(lead.get("lead_id", ""))
            )
            for lead in leads
        ]

    def _rule_qualify_single(
        self, lead: dict, audit: Optional[dict]
    ) -> dict:
        score = self._calculate_score(lead, audit)
        lead["lead_score"] = score
        lead["priority"] = self._determine_priority(score)
        lead["recommended_service"] = self._recommend_service(
            lead, score
        )
        return lead

    def _calculate_score(
        self, lead: dict, audit: Optional[dict]
    ) -> int:
        score = 30

        if lead.get("website"):
            score += 15
        if lead.get("contact_name"):
            score += 10
        if lead.get("profile_urls"):
            score += 10
        if lead.get("rating", 0) >= 4.0:
            score += 10
        if lead.get("review_count", 0) > 10:
            score += 5

        if audit:
            if audit.get("mobile_responsive"):
                score += 5
            if audit.get("has_lead_capture"):
                score += 5
            if audit.get("has_chat_support"):
                score += 5
            if audit.get("has_booking_system"):
                score += 5
            score += (audit.get("overall_quality", 0) // 10)

        return min(score, 100)

    def _determine_priority(self, score: int) -> str:
        if score >= 70:
            return "High"
        elif score >= 40:
            return "Medium"
        return "Low"

    def _recommend_service(
        self, lead: dict, score: int
    ) -> str:
        name = (lead.get("company_name", "") + lead.get("notes", "")).lower()
        if score >= 70:
            if any(w in name for w in ["ai", "chatbot", "automation"]):
                return "AI Automation Solutions"
            if any(w in name for w in ["market", "advert", "seo"]):
                return "Digital Marketing"
            return "Website Design & Development"
        elif score >= 40:
            if not lead.get("website"):
                return "Website Design & Development"
            return "SEO Services"
        return "Digital Marketing"

    def _build_llm_prompt(
        self, lead: dict, audit: Optional[dict]
    ) -> str:
        company = lead.get("company_name", "Unknown")
        industry = lead.get("industry", "Unknown")
        website = lead.get("website", "None")
        rating = lead.get("rating", 0)
        reviews = lead.get("review_count", 0)

        audit_info = ""
        if audit:
            audit_info = (
                f"Mobile: {audit.get('mobile_responsive')}, "
                f"Lead Capture: {audit.get('has_lead_capture')}, "
                f"Chat: {audit.get('has_chat_support')}, "
                f"Quality: {audit.get('overall_quality')}/100"
            )

        return (
            f"Qualify this lead for a digital services agency.\n"
            f"Company: {company}\nIndustry: {industry}\n"
            f"Website: {website}\nRating: {rating}/5 ({reviews} reviews)\n"
            f"Audit: {audit_info}\n\n"
            f"Available services: {', '.join(SERVICES)}\n\n"
            f"Return JSON: {{\n"
            f'  "lead_score": <0-100>,\n'
            f'  "priority": "<Low|Medium|High>",\n'
            f'  "recommended_service": "<best service>"\n'
            f"}}"
        )
