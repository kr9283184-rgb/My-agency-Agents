from typing import Optional
import requests
from urllib.parse import urlparse

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


class WebScraper:
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }
        )

    def fetch(self, url: str) -> Optional[str]:
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException:
            return None

    def fetch_soup(self, url: str) -> Optional[BeautifulSoup]:
        if BeautifulSoup is None:
            return None
        html = self.fetch(url)
        if html:
            return BeautifulSoup(html, "lxml")
        return None

    def extract_text(self, url: str) -> str:
        soup = self.fetch_soup(url)
        if soup is None:
            return ""
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:5000]

    def check_mobile(self, url: str) -> bool:
        soup = self.fetch_soup(url)
        if soup is None:
            return False
        meta = soup.find("meta", attrs={"name": "viewport"})
        return meta is not None

    def check_element_exists(
        self, url: str, tag: str, attrs: dict
    ) -> bool:
        soup = self.fetch_soup(url)
        if soup is None:
            return False
        return soup.find(tag, attrs=attrs) is not None

    def has_lead_capture(self, url: str) -> bool:
        soup = self.fetch_soup(url)
        if soup is None:
            return False
        keywords = [
            "contact", "newsletter", "sign up", "subscribe",
            "get started", "free quote", "book now", "schedule",
        ]
        text = soup.get_text().lower() if soup else ""
        return any(k in text for k in keywords)

    def has_chat(self, url: str) -> bool:
        soup = self.fetch_soup(url)
        if soup is None:
            return False
        text = str(soup).lower()
        chat_keywords = [
            "chat", "intercom", "tidio", "livechat", "drift",
            "crisp", "hubspot", "zendesk",
        ]
        return any(k in text for k in chat_keywords)

    def has_booking(self, url: str) -> bool:
        soup = self.fetch_soup(url)
        if soup is None:
            return False
        text = str(soup).lower()
        booking_keywords = [
            "book", "appointment", "schedule", "calendly",
            "reserve", "booking",
        ]
        return any(k in text for k in booking_keywords)

    def get_social_links(self, url: str) -> dict:
        soup = self.fetch_soup(url)
        if soup is None:
            return {}
        social = {}
        platforms = {
            "facebook": "facebook.com",
            "instagram": "instagram.com",
            "linkedin": "linkedin.com",
            "twitter": ["twitter.com", "x.com"],
            "youtube": "youtube.com",
        }
        for a in soup.find_all("a", href=True):
            href = a["href"].lower()
            for name, domains in platforms.items():
                if isinstance(domains, str):
                    domains = [domains]
                if any(d in href for d in domains):
                    if name not in social:
                        social[name] = a["href"]
        return social

    def extract_domain(self, url: str) -> str:
        parsed = urlparse(url)
        return parsed.netloc or parsed.path.split("/")[0]
