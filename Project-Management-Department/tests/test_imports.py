def test_project_management_package_imports():
    from project_management.config import Config
    from project_management.database import ProjectDatabase
    from project_management.orchestrator import ProjectOrchestrator, ProjectResult
    from project_management.cli import main
    assert Config is not None
    assert ProjectDatabase is not None
    assert ProjectOrchestrator is not None
    assert ProjectResult is not None
    assert callable(main)


def test_agents_imports():
    from project_management.agents.base_agent import BaseAgent
    from project_management.agents.planning_agent import PlanningAgent
    from project_management.agents.resource_allocation_agent import ResourceAllocationAgent
    from project_management.agents.task_management_agent import TaskManagementAgent
    from project_management.agents.team_coordination_agent import TeamCoordinationAgent
    from project_management.agents.progress_tracking_agent import ProgressTrackingAgent
    from project_management.agents.risk_management_agent import RiskManagementAgent
    from project_management.agents.change_request_agent import ChangeRequestAgent
    from project_management.agents.budget_profitability_agent import BudgetProfitabilityAgent
    from project_management.agents.client_communication_agent import ClientCommunicationAgent
    from project_management.agents.quality_coordination_agent import QualityCoordinationAgent
    from project_management.agents.delivery_management_agent import DeliveryManagementAgent
    from project_management.agents.knowledge_management_agent import KnowledgeManagementAgent
    from project_management.agents.project_director_agent import ProjectDirectorAgent
    assert BaseAgent is not None
    assert PlanningAgent is not None
    assert ResourceAllocationAgent is not None
    assert TaskManagementAgent is not None
    assert TeamCoordinationAgent is not None
    assert ProgressTrackingAgent is not None
    assert RiskManagementAgent is not None
    assert ChangeRequestAgent is not None
    assert BudgetProfitabilityAgent is not None
    assert ClientCommunicationAgent is not None
    assert QualityCoordinationAgent is not None
    assert DeliveryManagementAgent is not None
    assert KnowledgeManagementAgent is not None
    assert ProjectDirectorAgent is not None


def test_email_templates_import():
    from project_management.email.templates import (
        WEEKLY_UPDATE_TEMPLATE,
        MILESTONE_COMPLETE_TEMPLATE,
        DELIVERY_NOTIFICATION_TEMPLATE,
        DELAY_NOTIFICATION_TEMPLATE,
    )
    assert WEEKLY_UPDATE_TEMPLATE is not None
    assert MILESTONE_COMPLETE_TEMPLATE is not None
    assert DELIVERY_NOTIFICATION_TEMPLATE is not None
    assert DELAY_NOTIFICATION_TEMPLATE is not None
