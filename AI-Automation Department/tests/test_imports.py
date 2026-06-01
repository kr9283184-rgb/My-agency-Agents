def test_package_imports():
    from ai_automation.config import Config
    from ai_automation.database import AutomationDatabase
    from ai_automation.orchestrator import AutomationOrchestrator, AutomationResult
    from ai_automation.cli import main

    assert Config is not None
    assert AutomationDatabase is not None
    assert AutomationOrchestrator is not None
    assert AutomationResult is not None
    assert callable(main)


def test_agent_imports():
    from ai_automation.agents.base_agent import BaseAgent
    from ai_automation.agents.automation_director_agent import AutomationDirectorAgent
    from ai_automation.agents.specialists import (
        SolutionArchitectAgent,
        WorkflowAutomationEngineer,
        AIModelEngineerAgent,
        TestingValidationAgent,
    )

    assert BaseAgent is not None
    assert AutomationDirectorAgent is not None
    assert SolutionArchitectAgent is not None
    assert WorkflowAutomationEngineer is not None
    assert AIModelEngineerAgent is not None
    assert TestingValidationAgent is not None
