from typing import Optional
from client_outreach.agents.base_agent import BaseAgent
from client_outreach.llm.base import LLMProvider


class LeadIntelligenceAgent(BaseAgent):
    def __init__(self, llm: Optional[LLMProvider] = None, **kwargs):
        super().__init__(**kwargs)
        self.llm = llm

    def research_lead(self, lead: dict) -> dict:
        lead_id = lead.get("lead_id", "")
        company = lead.get("company_name", "")
        industry = lead.get("industry", "")
        website = lead.get("website", "")
        location = lead.get("location", "")

        brief = self._generate_brief(lead) if self.llm else self._rule_brief(lead)

        brief["lead_id"] = lead_id
        brief["company_name"] = company
        import json
        self.db.update_lead(lead_id, {
            "notes": json.dumps(brief),
            "pipeline_stage": "New Lead",
        })
        self.log(f"Researched {company} — intent: {brief.get('buying_intent', 'unknown')}")
        return brief

    def _generate_brief(self, lead: dict) -> dict:
        prompt = (
            f"Analyze this sales lead and generate a personalized brief.\n\n"
            f"Company: {lead.get('company_name', '')}\n"
            f"Industry: {lead.get('industry', '')}\n"
            f"Location: {lead.get('location', '')}\n"
            f"Website: {lead.get('website', '')}\n"
            f"Contact: {lead.get('contact_name', '')} ({lead.get('job_title', '')})\n\n"
            f"Return a JSON object with:\n"
            f"- pain_points: list of likely pain points\n"
            f"- service_fit: what services they likely need\n"
            f"- buying_intent: 'low', 'medium', or 'high'\n"
            f"- recommended_approach: brief strategy for outreach\n"
            f"- talking_points: list of key talking points"
        )
        result = self.llm.generate_json(prompt)
        import json
        try:
            return json.loads(result)
        except (json.JSONDecodeError, TypeError):
            return self._rule_brief(lead)

    def _rule_brief(self, lead: dict) -> dict:
        industry = (lead.get("industry", "") or "").lower()
        if "real estate" in industry:
            pain_points = [
                "Low-quality leads from traditional advertising",
                "Time wasted on cold calling unqualified prospects",
                "Difficulty tracking lead sources and ROI",
            ]
            service_fit = "AI lead generation, CRM automation, website lead capture"
            intent = "high"
        elif "dentist" in industry or "medical" in industry:
            pain_points = [
                "Patients finding competitors online",
                "No-show appointments hurting revenue",
                "Outdated website with poor mobile experience",
            ]
            service_fit = "Website redesign, SEO, appointment booking system"
            intent = "medium"
        else:
            pain_points = [
                "Limited online presence",
                "Manual lead tracking",
                "Missed follow-up opportunities",
            ]
            service_fit = "Digital marketing, CRM setup, automation"
            intent = "medium"

        return {
            "pain_points": pain_points,
            "service_fit": service_fit,
            "buying_intent": intent,
            "recommended_approach": (
                f"Start with personalized email highlighting specific pain points, "
                f"follow up with relevant case study at day 3"
            ),
            "talking_points": [
                "Increase lead quality and quantity",
                "Automate follow-up processes",
                "Track ROI across all channels",
            ],
        }

    def enrich_lead_with_website(self, lead: dict) -> dict:
        website = lead.get("website", "")
        if not website:
            return lead
        try:
            import requests
            from bs4 import BeautifulSoup
            resp = requests.get(website, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "lxml")
                texts = soup.get_text(separator=" ", strip=True)[:2000]
                lead["website_snippet"] = texts
                if soup.find("form") or soup.select("input[type=email]"):
                    lead["has_lead_capture"] = True
                if soup.select(".chat, #chat, [class*=chat], iframe[src*=calendly]"):
                    lead["has_booking"] = True
        except Exception as e:
            self.log(f"Could not scrape {website}: {e}")
        return lead
