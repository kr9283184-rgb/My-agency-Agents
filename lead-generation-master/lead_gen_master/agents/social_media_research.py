from typing import Optional
from lead_gen_master.agents.base_agent import BaseAgent
from lead_gen_master.search.web_scraper import WebScraper


class SocialMediaResearchAgent(BaseAgent):
    def __init__(self, memory=None):
        super().__init__(memory)
        self.scraper = WebScraper()

    def analyze_social_presence(
        self, website: str
    ) -> dict:
        self.log(f"Analyzing social presence for {website}")
        social_links = self.scraper.get_social_links(website)

        presence = {
            "website": website,
            "facebook": social_links.get("facebook", ""),
            "instagram": social_links.get("instagram", ""),
            "linkedin": social_links.get("linkedin", ""),
            "twitter": social_links.get("twitter", ""),
            "youtube": social_links.get("youtube", ""),
            "platforms_found": len(social_links),
            "has_social_presence": len(social_links) >= 2,
        }
        return presence

    def enrich_leads(self, leads: list[dict]) -> list[dict]:
        self.log(
            f"Adding social presence data to {len(leads)} leads"
        )
        for lead in leads:
            website = lead.get("website", "")
            if website:
                social = self.analyze_social_presence(website)
                lead["profile_urls"] = (
                    lead.get("profile_urls", "")
                    or "; ".join(
                        v
                        for v in [
                            social.get("facebook", ""),
                            social.get("linkedin", ""),
                            social.get("instagram", ""),
                        ]
                        if v
                    )
                )
                lead["notes"] += (
                    f"\nSocial platforms: {social['platforms_found']}"
                )
        return leads
