from typing import Optional
import requests

from lead_gen_master.config import Config


BRAVE_WEB_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"


class BraveSearch:
    def __init__(self):
        self.api_key = Config.BRAVE_API_KEY

    def is_available(self) -> bool:
        return bool(self.api_key)

    def search(
        self,
        query: str,
        count: int = 10,
        offset: int = 0,
    ) -> list[dict]:
        if not self.is_available():
            return []

        try:
            resp = requests.get(
                BRAVE_WEB_SEARCH_URL,
                headers={
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip",
                    "X-Subscription-Token": self.api_key,
                },
                params={
                    "q": query,
                    "count": min(count, 20),
                    "offset": offset,
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            results = []
            for item in data.get("web", {}).get("results", []):
                results.append(
                    {
                        "title": item.get("title", ""),
                        "link": item.get("url", ""),
                        "snippet": item.get("description", ""),
                        "source": "brave_search",
                    }
                )
            return results
        except requests.RequestException:
            return []

    def search_businesses(
        self,
        industry: str,
        location: str,
        count: int = 10,
    ) -> list[dict]:
        query = f"{industry} in {location}"
        return self.search(query, count=count)

    def search_linkedin(
        self, company_name: str
    ) -> list[dict]:
        query = f"{company_name} LinkedIn"
        return self.search(query, count=5)
