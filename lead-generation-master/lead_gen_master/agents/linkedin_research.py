from typing import Optional
from lead_gen_master.agents.base_agent import BaseAgent
from lead_gen_master.search.brave_search import BraveSearch
from lead_gen_master.llm.base import LLMProvider


class LinkedInResearchAgent(BaseAgent):
    def __init__(
        self,
        llm: Optional[LLMProvider] = None,
        memory=None,
    ):
        super().__init__(memory)
        self.llm = llm
        self.search = BraveSearch()

    def find_decision_makers(
        self,
        company_name: str,
        industry: str = "",
    ) -> list[dict]:
        self.log(f"Searching decision makers at {company_name}")

        results = self.search.search_linkedin(company_name)
        profiles = []

        for r in results:
            link = r.get("link", "")
            title = r.get("title", "")
            snippet = r.get("snippet", "")

            if "linkedin.com" not in link.lower():
                continue

            profile = {
                "company_name": company_name,
                "profile_url": link,
                "title": title,
                "snippet": snippet,
                "name": "",
                "job_title": "",
            }

            if self.llm and self.llm.is_available():
                enriched = self._enrich_profile(
                    title, snippet
                )
                profile.update(enriched)

            profiles.append(profile)

        return profiles

    def _enrich_profile(
        self, title: str, snippet: str
    ) -> dict:
        prompt = (
            f"Extract the person's name and job title from this LinkedIn result.\n"
            f"Title: {title}\nSnippet: {snippet}\n\n"
            f"Return JSON: {{\"name\": \"...\", \"job_title\": \"...\"}}\n"
            f"If unknown, use empty strings."
        )
        result = self.llm.generate_json(prompt)
        try:
            import json
            return json.loads(
                result.replace("```json", "").replace("```", "").strip()
            )
        except (json.JSONDecodeError, AttributeError):
            return {"name": "", "job_title": ""}

    def enrich_leads(self, leads: list[dict]) -> list[dict]:
        self.log(f"Enriching {len(leads)} leads with LinkedIn data")
        enriched = []
        for lead in leads:
            profiles = self.find_decision_makers(
                lead.get("company_name", ""),
                lead.get("industry", ""),
            )
            if profiles:
                lead["profile_urls"] = (
                    profiles[0].get("profile_url", "")
                )
                lead["contact_name"] = (
                    profiles[0].get("name", "")
                )
                lead["job_title"] = (
                    profiles[0].get("job_title", "")
                )
            enriched.append(lead)
        return enriched
