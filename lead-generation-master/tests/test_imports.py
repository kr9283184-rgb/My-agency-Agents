def test_import_orchestrator():
    from lead_gen_master import Orchestrator, LeadDatabase
    assert Orchestrator
    assert LeadDatabase


def test_import_config():
    from lead_gen_master.config import Config
    assert Config
    assert hasattr(Config, "OUTPUT_DIR")


def test_import_memory():
    from lead_gen_master.memory import MemoryManager
    from lead_gen_master.memory.schemas import Lead
    assert MemoryManager
    assert Lead


def test_import_llm():
    from lead_gen_master.llm import (
        LLMProvider, GroqProvider, OpenAIProvider, OllamaProvider,
    )
    assert LLMProvider
    assert GroqProvider
    assert OpenAIProvider
    assert OllamaProvider


def test_import_search():
    from lead_gen_master.search import (
        GoogleCustomSearch, BraveSearch, SerpAPISearch, WebScraper,
    )
    assert GoogleCustomSearch
    assert BraveSearch
    assert SerpAPISearch
    assert WebScraper


def test_import_agents():
    from lead_gen_master.agents.market_intelligence import (
        MarketIntelligenceAgent,
    )
    from lead_gen_master.agents.google_business_research import (
        GoogleBusinessResearchAgent,
    )
    from lead_gen_master.agents.linkedin_research import (
        LinkedInResearchAgent,
    )
    from lead_gen_master.agents.social_media_research import (
        SocialMediaResearchAgent,
    )
    from lead_gen_master.agents.website_audit import (
        WebsiteAuditAgent,
    )
    from lead_gen_master.agents.lead_qualification import (
        LeadQualificationAgent,
    )
    from lead_gen_master.agents.duplicate_detection import (
        DuplicateDetectionAgent,
    )
    from lead_gen_master.agents.crm_management import (
        CRMManagementAgent,
    )
    from lead_gen_master.agents.sales_intelligence import (
        SalesIntelligenceAgent,
    )
    from lead_gen_master.agents.excel_reporting import (
        ExcelReportingAgent,
    )
    from lead_gen_master.agents.executive_report import (
        ExecutiveReportAgent,
    )
    assert MarketIntelligenceAgent
    assert GoogleBusinessResearchAgent
    assert LinkedInResearchAgent
    assert SocialMediaResearchAgent
    assert WebsiteAuditAgent
    assert LeadQualificationAgent
    assert DuplicateDetectionAgent
    assert CRMManagementAgent
    assert SalesIntelligenceAgent
    assert ExcelReportingAgent
    assert ExecutiveReportAgent
