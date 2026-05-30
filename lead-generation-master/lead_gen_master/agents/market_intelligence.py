import json
import re
from typing import Optional
from lead_gen_master.agents.base_agent import BaseAgent
from lead_gen_master.llm.base import LLMProvider
from lead_gen_master.search.brave_search import BraveSearch


class MarketIntelligenceAgent(BaseAgent):
    def __init__(
        self,
        llm: Optional[LLMProvider] = None,
        memory=None,
    ):
        super().__init__(memory)
        self.llm = llm
        self.search = BraveSearch()

    def analyze_industry(
        self,
        industry: str,
        location: str = "",
    ) -> dict:
        self.log(f"Analyzing market: {industry} in {location}")

        existing = [
            i
            for i in self.memory.get_industries()
            if i.get("industry", "").lower() == industry.lower()
        ]
        if existing:
            self.log(f"Found cached industry insight for {industry}")
            return existing[0]

        search_results = self.search.search_businesses(
            industry, location, count=5
        )

        if self.llm and self.llm.is_available():
            insight = self._llm_analysis(
                industry, location, search_results
            )
        else:
            insight = self._rule_analysis(
                industry, search_results
            )

        self.memory.add_industry(insight)
        return insight

    def _llm_analysis(
        self,
        industry: str,
        location: str,
        search_results: list[dict],
    ) -> dict:
        snippets = "\n".join(
            r.get("snippet", "") for r in search_results[:5]
        )
        prompt = (
            f"Analyze the '{industry}' market in '{location}' for digital services.\n\n"
            f"Search snippets:\n{snippets}\n\n"
            f"Return JSON: {{\n"
            f'  "industry": "{industry}",\n'
            f'  "demand_score": <0-100>,\n'
            f'  "growth_potential": "<Low|Medium|High>",\n'
            f'  "recommended_services": ["service1", "service2", ...],\n'
            f'  "notes": "<brief analysis>"\n'
            f"}}"
        )
        result = self.llm.generate_json(prompt)
        try:
            cleaned = re.sub(
                r"^```(?:json)?\s*|\s*```$", "", result, flags=re.DOTALL
            )
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {
                "industry": industry,
                "demand_score": 50,
                "growth_potential": "Medium",
                "recommended_services": [
                    "Website Design",
                    "SEO",
                    "Digital Marketing",
                ],
                "notes": "LLM analysis unavailable; used defaults.",
            }

    def _rule_analysis(
        self,
        industry: str,
        search_results: list[dict],
    ) -> dict:
        result_count = len(search_results)
        return {
            "industry": industry,
            "demand_score": min(result_count * 10, 80),
            "growth_potential": "Medium",
            "recommended_services": [
                "Website Design",
                "SEO",
                "Digital Marketing",
            ],
            "notes": f"Found {result_count} relevant results.",
        }

    def recommend_industries(self) -> list[str]:
        return [
            "real estate agents",
            "dentists",
            "auto repair shops",
            "law firms",
            "restaurants",
            "medical spas",
            "roofing contractors",
            "plumbing services",
            "gyms and fitness centers",
            "home renovation contractors",
        ]
