import json
import re
from typing import Optional
from lead_gen_master.agents.base_agent import BaseAgent
from lead_gen_master.search.google_custom_search import GoogleCustomSearch
from lead_gen_master.search.brave_search import BraveSearch
from lead_gen_master.search.serpapi_search import SerpAPISearch
from lead_gen_master.llm.base import LLMProvider


class GoogleBusinessResearchAgent(BaseAgent):
    def __init__(
        self,
        llm: Optional[LLMProvider] = None,
        memory=None,
    ):
        super().__init__(memory)
        self.llm = llm
        self.google = GoogleCustomSearch()
        self.brave = BraveSearch()
        self.serpapi = SerpAPISearch()

    def find_businesses(
        self,
        industry: str,
        location: str,
        max_results: int = 25,
    ) -> list[dict]:
        self.log(
            f"Searching for {industry} in {location} "
            f"(max {max_results})"
        )

        businesses = []

        if self.google.is_available():
            results = self.google.search_businesses(
                industry, location, num=min(max_results, 10)
            )
            for r in results:
                biz = self._parse_result(r, industry, location)
                if biz:
                    businesses.append(biz)

        if len(businesses) < max_results and self.brave.is_available():
            results = self.brave.search_businesses(
                industry, location,
                count=min(max_results - len(businesses) + 5, 20),
            )
            for r in results:
                biz = self._parse_result(r, industry, location)
                if biz and biz["company_name"] not in [
                    b["company_name"] for b in businesses
                ]:
                    businesses.append(biz)

        if len(businesses) < max_results and self.serpapi.is_available():
            results = self.serpapi.search_businesses(
                industry, location,
                num=min(max_results - len(businesses) + 5, 10),
            )
            for r in results:
                biz = self._parse_result(r, industry, location)
                if biz and biz["company_name"] not in [
                    b["company_name"] for b in businesses
                ]:
                    businesses.append(biz)

        self.log(f"Found {len(businesses)} businesses")
        self.memory.add_leads(businesses)
        return businesses

    def _parse_result(
        self,
        result: dict,
        industry: str,
        location: str,
    ) -> Optional[dict]:
        title = result.get("title", "").strip()
        link = result.get("link", "").strip()
        snippet = result.get("snippet", "").strip()

        if not title:
            return None

        company_name = self._extract_company_name(title, link)

        return {
            "lead_id": f"lead_{hash(link or title) & 0xFFFFFF:06x}",
            "company_name": company_name,
            "industry": industry,
            "contact_name": "",
            "job_title": "",
            "website": link if link.startswith("http") else "",
            "profile_urls": "",
            "location": location,
            "rating": 0.0,
            "review_count": 0,
            "lead_score": 0,
            "priority": "Low",
            "recommended_service": "",
            "notes": snippet[:500] if snippet else "",
            "source": result.get("source", "search"),
            "created_at": __import__(
                "datetime", fromlist=["datetime"]
            ).datetime.now().isoformat(),
        }

    def _extract_company_name(
        self, title: str, link: str
    ) -> str:
        if self.llm and self.llm.is_available():
            prompt = (
                f"Extract the business/company name from this search result.\n"
                f"Title: {title}\nURL: {link}\n"
                f"Return ONLY the company name, nothing else."
            )
            name = self.llm.generate(
                prompt, temperature=0.1, max_tokens=50
            ).strip()
            if name and not name.startswith("["):
                return name[:100]
        cleaned = re.sub(r"\s*[-–|].*$", "", title).strip()
        return cleaned[:100] if cleaned else "Unknown"
