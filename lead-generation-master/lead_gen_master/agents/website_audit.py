from typing import Optional
from lead_gen_master.agents.base_agent import BaseAgent
from lead_gen_master.search.web_scraper import WebScraper
from lead_gen_master.llm.base import LLMProvider


class WebsiteAuditAgent(BaseAgent):
    def __init__(
        self,
        llm: Optional[LLMProvider] = None,
        memory=None,
    ):
        super().__init__(memory)
        self.llm = llm
        self.scraper = WebScraper()

    def audit(self, website: str, company_name: str = "") -> dict:
        self.log(f"Auditing website: {website}")

        mobile = self.scraper.check_mobile(website)
        has_capture = self.scraper.has_lead_capture(website)
        has_chat = self.scraper.has_chat(website)
        has_booking = self.scraper.has_booking(website)

        page_text = self.scraper.extract_text(website)
        content_quality = self._score_content(page_text)

        if self.llm and self.llm.is_available() and page_text:
            quality = self._llm_quality_score(
                page_text, company_name
            )
        else:
            quality = content_quality

        audit = {
            "lead_id": "",
            "company_name": company_name,
            "website": website,
            "mobile_responsive": mobile,
            "has_lead_capture": has_capture,
            "has_booking_system": has_booking,
            "has_chat_support": has_chat,
            "seo_basics_score": content_quality,
            "load_speed_rating": "Unknown",
            "overall_quality": quality,
            "notes": self._build_notes(
                mobile, has_capture, has_chat, has_booking
            ),
            "created_at": __import__(
                "datetime", fromlist=["datetime"]
            ).datetime.now().isoformat(),
        }
        return audit

    def audit_leads(self, leads: list[dict]) -> list[dict]:
        self.log(f"Auditing websites for {len(leads)} leads")
        audits = []
        for lead in leads:
            website = lead.get("website", "")
            if website:
                audit = self.audit(
                    website,
                    lead.get("company_name", ""),
                )
                audit["lead_id"] = lead.get("lead_id", "")
                audits.append(audit)
        self.memory.add_audits(audits)
        return audits

    def _score_content(self, text: str) -> int:
        if not text:
            return 0
        score = 30
        keywords = [
            "about", "service", "contact", "blog", "portfolio",
            "testimonial", "faq", "price",
        ]
        for kw in keywords:
            if kw in text.lower():
                score += 8
        return min(score, 100)

    def _llm_quality_score(
        self, page_text: str, company_name: str
    ) -> int:
        prompt = (
            f"Rate the website quality of '{company_name}' from 0-100.\n"
            f"Consider: design, content quality, professionalism, clarity.\n\n"
            f"Page content (first 2000 chars):\n{page_text[:2000]}\n\n"
            f"Return ONLY a number 0-100."
        )
        result = self.llm.generate(
            prompt, temperature=0.2, max_tokens=10
        ).strip()
        try:
            return max(0, min(100, int(result)))
        except (ValueError, TypeError):
            return 50

    def _build_notes(
        self,
        mobile: bool,
        capture: bool,
        chat: bool,
        booking: bool,
    ) -> str:
        notes = []
        if not mobile:
            notes.append("Not mobile-responsive")
        if not capture:
            notes.append("No lead capture form found")
        if not chat:
            notes.append("No chat support")
        if not booking:
            notes.append("No booking system")
        if not notes:
            notes.append("Good digital presence")
        return "; ".join(notes)
