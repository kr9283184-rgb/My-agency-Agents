def test_package_imports():
    from website_development.config import Config
    from website_development.database import WebsiteDatabase
    from website_development.orchestrator import WebsiteOrchestrator, WebsiteResult
    from website_development.cli import main

    assert Config is not None
    assert WebsiteDatabase is not None
    assert WebsiteOrchestrator is not None
    assert WebsiteResult is not None
    assert callable(main)


def test_agent_imports():
    from website_development.agents.base_agent import BaseAgent
    from website_development.agents.website_director_agent import WebsiteDevelopmentDirectorAgent
    from website_development.agents.specialists import (
        BusinessAnalysisAgent,
        UIUXDesignDirectorAgent,
        FrontendDevelopmentAgent,
        QATestingAgent,
    )

    assert BaseAgent is not None
    assert WebsiteDevelopmentDirectorAgent is not None
    assert BusinessAnalysisAgent is not None
    assert UIUXDesignDirectorAgent is not None
    assert FrontendDevelopmentAgent is not None
    assert QATestingAgent is not None
