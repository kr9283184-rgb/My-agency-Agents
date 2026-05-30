from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime


@dataclass
class Lead:
    lead_id: str
    company_name: str
    industry: str = ""
    contact_name: str = ""
    job_title: str = ""
    website: str = ""
    profile_urls: str = ""
    location: str = ""
    rating: float = 0.0
    review_count: int = 0
    lead_score: int = 0
    priority: str = "Low"
    recommended_service: str = ""
    notes: str = ""
    source: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return asdict(self)


@dataclass
class IndustryInsight:
    industry: str
    demand_score: int
    growth_potential: str
    recommended_services: list = field(default_factory=list)
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return asdict(self)


@dataclass
class WebsiteAudit:
    lead_id: str
    company_name: str
    website: str
    mobile_responsive: bool = False
    has_lead_capture: bool = False
    has_booking_system: bool = False
    has_chat_support: bool = False
    seo_basics_score: int = 0
    load_speed_rating: str = "Unknown"
    overall_quality: int = 0
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return asdict(self)


@dataclass
class SalesBrief:
    lead_id: str
    company_name: str
    pain_points: list = field(default_factory=list)
    outreach_ideas: list = field(default_factory=list)
    recommended_services: list = field(default_factory=list)
    opportunity_summary: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return asdict(self)
