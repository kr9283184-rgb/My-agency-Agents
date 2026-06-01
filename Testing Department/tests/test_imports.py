def test_package_imports():
    from testing_department.config import Config
    from testing_department.database import TestingDatabase
    from testing_department.orchestrator import TestingOrchestrator, TestingResult
    from testing_department.cli import main

    assert Config is not None
    assert TestingDatabase is not None
    assert TestingOrchestrator is not None
    assert TestingResult is not None
    assert callable(main)


def test_agent_imports():
    from testing_department.agents.base_agent import BaseAgent
    from testing_department.agents.qa_director_agent import QADirectorAgent
    from testing_department.agents.specialists import (
        RequirementValidationAgent,
        FunctionalTestingAgent,
        AISystemTestingAgent,
        PerformanceTestingAgent,
        ReleaseApprovalAgent,
    )

    assert BaseAgent is not None
    assert QADirectorAgent is not None
    assert RequirementValidationAgent is not None
    assert FunctionalTestingAgent is not None
    assert AISystemTestingAgent is not None
    assert PerformanceTestingAgent is not None
    assert ReleaseApprovalAgent is not None
