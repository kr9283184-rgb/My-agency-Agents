from typing import Optional
import requests

from lead_gen_master.config import Config


class GoogleCustomSearch:
    def __init__(self):
        self.api_key = Config.GOOGLE_API_KEY
        self.cse_id = Config.GOOGLE_CSE_ID
        self.base_url = "https://www.googleapis.com/customsearch/v1"

    def is_available(self) -> bool:
        return bool(self.api_key and self.cse_id)

    def search(
        self,
        query: str,
        num: int = 10,
        start: int = 1,
    ) -> list[dict]:
        if not self.is_available():
            return []

        try:
            resp = requests.get(
                self.base_url,
                params={
                    "key": self.api_key,
                    "cx": self.cse_id,
                    "q": query,
                    "num": min(num, 10),
                    "start": start,
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            items = data.get("items", [])
            results = []
            for item in items:
                results.append(
                    {
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "source": "google_custom_search",
                    }
                )
            return results
        except requests.RequestException:
            return []

    def search_businesses(
        self,
        industry: str,
        location: str,
        num: int = 10,
    ) -> list[dict]:
        query = f"{industry} in {location}"
        return self.search(query, num=num)

    def search_website(self, domain: str) -> list[dict]:
        query = f"site:{domain}"
        return self.search(query, num=5)
