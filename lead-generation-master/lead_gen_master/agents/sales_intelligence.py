import json
import re
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


class SalesIntelligenceAgent(BaseAgent):
    def __init__(
        self,
        llm: Optional[LLMProvider] = None,
        memory=None,
    ):
        super().__init__(memory)
        self.llm = llm

    def generate_brief(self, lead: dict) -> dict:
        self.log(
            f"Generating sales brief for {lead.get('company_name', '')}"
        )

        if self.llm and self.llm.is_available():
            brief = self._llm_brief(lead)
        else:
            brief = self._rule_brief(lead)

        self.memory.add_outreach(brief)
        return brief

    def generate_briefs(
        self, leads: list[dict]
    ) -> list[dict]:
        self.log(
            f"Generating sales briefs for {len(leads)} leads"
        )
        briefs = []
        for lead in leads:
            brief = self.generate_brief(lead)
            briefs.append(brief)
        self.memory.add_outreaches(briefs)
        return briefs

    def _llm_brief(self, lead: dict) -> dict:
        prompt = (
            f"Generate a sales brief for this lead.\n\n"
            f"Company: {lead.get('company_name', '')}\n"
            f"Industry: {lead.get('industry', '')}\n"
            f"Website: {lead.get('website', '')}\n"
            f"Score: {lead.get('lead_score', 0)}/100\n"
            f"Priority: {lead.get('priority', 'Low')}\n\n"
            f"Available services: {', '.join(SERVICES)}\n\n"
            f"Return JSON: {{\n"
            f'  "lead_id": "{lead.get("lead_id", "")}",\n'
            f'  "company_name": "{lead.get("company_name", "")}",\n'
            f'  "pain_points": ["point1", "point2", ...],\n'
            f'  "outreach_ideas": ["idea1", "idea2", ...],\n'
            f'  "recommended_services": ["service1", ...],\n'
            f'  "opportunity_summary": "<2-3 sentence summary>"\n'
            f"}}"
        )
        result = self.llm.generate_json(prompt)
        try:
            cleaned = re.sub(
                r"^```(?:json)?\s*|\s*```$",
                "",
                result,
                flags=re.DOTALL,
            )
            return json.loads(cleaned)
        except (json.JSONDecodeError, AttributeError):
            return self._rule_brief(lead)

    def _rule_brief(self, lead: dict) -> dict:
        score = lead.get("lead_score", 0)
        company = lead.get("company_name", "Unknown")
        industry = lead.get("industry", "a business")

        pain_points = [
            f"May need improved online presence",
            "Could benefit from lead generation automation",
        ]
        if score < 50:
            pain_points.append("Website may need modernization")

        outreach_ideas = [
            f"Personalized email highlighting relevant case studies",
            f"Offer free website audit or consultation",
        ]

        return {
            "lead_id": lead.get("lead_id", ""),
            "company_name": company,
            "pain_points": pain_points,
            "outreach_ideas": outreach_ideas,
            "recommended_services": [
                lead.get("recommended_service", SERVICES[0])
            ],
            "opportunity_summary": (
                f"{company} is a {industry} business "
                f"with a lead score of {score}. "
                f"They could benefit from digital services."
            ),
        }
