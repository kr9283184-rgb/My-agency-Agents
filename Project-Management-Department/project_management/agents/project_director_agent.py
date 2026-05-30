from typing import Optional
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


class ProjectDirectorAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.planning_agent = PlanningAgent(db=self.db)
        self.resource_agent = ResourceAllocationAgent(db=self.db)
        self.task_agent = TaskManagementAgent(db=self.db)
        self.coordination_agent = TeamCoordinationAgent(db=self.db)
        self.progress_agent = ProgressTrackingAgent(db=self.db)
        self.risk_agent = RiskManagementAgent(db=self.db)
        self.change_agent = ChangeRequestAgent(db=self.db)
        self.budget_agent = BudgetProfitabilityAgent(db=self.db)
        self.comm_agent = ClientCommunicationAgent(db=self.db)
        self.quality_agent = QualityCoordinationAgent(db=self.db)
        self.delivery_agent = DeliveryManagementAgent(db=self.db)
        self.knowledge_agent = KnowledgeManagementAgent(db=self.db)

    def execute_project(self, project: dict, output_dir: str = "") -> dict:
        company = project.get("company_name", "Unknown")
        project_id = project.get("project_id", "")
        self.log(f"Starting project execution for {company} ({project_id})")

        self.db.add_project(project)
        self.db.update_project_status(project_id, "planning", 0.0)

        results = {}

        self.log(f"Phase 1/12: Creating project plan...")
        plan = self.planning_agent.create_project_plan(project, output_dir)
        results["plan"] = plan
        self.db.update_project_status(project_id, "resource_allocation", 5.0)

        self.log(f"Phase 2/12: Allocating resources...")
        resources = self.resource_agent.allocate_resources(project, output_dir)
        results["resources"] = resources
        self.db.update_project_status(project_id, "in_progress", 10.0)

        self.log(f"Phase 3/12: Initializing task management...")
        tasks = self.task_agent.manage_tasks(project, output_dir)
        results["tasks"] = tasks
        self.db.update_project_status(project_id, "in_progress", 15.0)

        self.log(f"Phase 4/12: Coordinating teams...")
        coordination = self.coordination_agent.coordinate_teams(project, output_dir)
        results["coordination"] = coordination

        self.log(f"Phase 5/12: Tracking initial progress...")
        progress = self.progress_agent.track_progress(project, output_dir, "daily")
        results["progress"] = progress
        self.db.update_project_status(project_id, "in_progress", 20.0)

        self.log(f"Phase 6/12: Identifying and managing risks...")
        risks = self.risk_agent.manage_risks(project, output_dir)
        results["risks"] = risks

        self.log(f"Phase 7/12: Setting up budget tracking...")
        budget = self.budget_agent.track_budget(project, output_dir)
        results["budget"] = budget

        self.log(f"Phase 8/12: Generating initial client update...")
        comm = self.comm_agent.generate_update(project, "weekly", output_dir)
        results["communication"] = comm

        self.log(f"Phase 9/12: Setting up quality checkpoints...")
        quality = self.quality_agent.verify_quality(project, output_dir)
        results["quality"] = quality
        self.db.update_project_status(project_id, "in_progress", 30.0)

        self.log(f"Phase 10/12: Preparing delivery package...")
        delivery = self.delivery_agent.prepare_delivery(project, output_dir)
        results["delivery"] = delivery
        self.db.update_project_status(project_id, "delivery_ready" if delivery["delivery_ready"] else "in_progress", 90.0)

        self.log(f"Phase 11/12: Capturing knowledge...")
        knowledge = self.knowledge_agent.capture_lessons(project, output_dir)
        results["knowledge"] = knowledge

        self.log(f"Phase 12/12: Completing project...")
        self.db.update_project_status(project_id, "completed", 100.0)

        self.log(f"Project execution completed for {company}")
        return results
