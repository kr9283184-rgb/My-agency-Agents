from typing import Optional
import requests

from lead_gen_master.config import Config


SERPAPI_URL = "https://serpapi.com/search"


class SerpAPISearch:
    def __init__(self):
        self.api_key = Config.SERPAPI_API_KEY

    def is_available(self) -> bool:
        return bool(self.api_key)

    def search(
        self,
        query: str,
        num: int = 10,
        engine: str = "google",
    ) -> list[dict]:
        if not self.is_available():
            return []

        try:
            resp = requests.get(
                SERPAPI_URL,
                params={
                    "q": query,
                    "api_key": self.api_key,
                    "engine": engine,
                    "num": min(num, 10),
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            results = []
            for item in data.get("organic_results", []):
                results.append(
                    {
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "source": "serpapi",
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
