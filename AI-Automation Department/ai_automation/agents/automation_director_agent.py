from ai_automation.agents.base_agent import BaseAgent
from ai_automation.agents.specialists import (
    SolutionArchitectAgent,
    MultiAgentSystemEngineer,
    WorkflowAutomationEngineer,
    ChatbotEngineerAgent,
    ReceptionistEngineerAgent,
    IntegrationEngineerAgent,
    DataEngineerAgent,
    AIModelEngineerAgent,
    MemorySystemEngineerAgent,
    TestingValidationAgent,
    SecurityComplianceAgent,
    DeploymentEngineerAgent,
    MonitoringAgent,
    MaintenanceAgent,
)


class AutomationDirectorAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.architect = SolutionArchitectAgent(db=self.db)
        self.multi_agent = MultiAgentSystemEngineer(db=self.db)
        self.workflow = WorkflowAutomationEngineer(db=self.db)
        self.chatbot = ChatbotEngineerAgent(db=self.db)
        self.receptionist = ReceptionistEngineerAgent(db=self.db)
        self.integration = IntegrationEngineerAgent(db=self.db)
        self.data = DataEngineerAgent(db=self.db)
        self.model = AIModelEngineerAgent(db=self.db)
        self.memory = MemorySystemEngineerAgent(db=self.db)
        self.testing = TestingValidationAgent(db=self.db)
        self.security = SecurityComplianceAgent(db=self.db)
        self.deployment = DeploymentEngineerAgent(db=self.db)
        self.monitoring = MonitoringAgent(db=self.db)
        self.maintenance = MaintenanceAgent(db=self.db)

    def execute_project(self, project: dict, output_dir: str) -> dict:
        project_id = project.get("project_id", "")
        company = project.get("company_name", "Unknown")
        self.log(f"Starting automation execution for {company} ({project_id})")

        self.db.add_project(project)
        self.db.update_status(project_id, "strategy", 5.0)

        results = {
            "execution_plan": self._create_execution_plan(project, output_dir)
        }
        self.db.add_output(project_id, "execution_plan", results["execution_plan"].get("file_path", ""))

        steps = [
            ("technical_architecture", self.architect.create_architecture, "architecture", 12.0),
            ("multi_agent_system", self.multi_agent.build_system_plan, "engineering", 20.0),
            ("workflow_package", self.workflow.create_workflows, "engineering", 28.0),
            ("chatbot_system", self.chatbot.build_chatbot_plan, "engineering", 36.0),
            ("ai_receptionist", self.receptionist.build_receptionist_plan, "engineering", 44.0),
            ("integration_package", self.integration.create_integration_package, "integration", 52.0),
            ("data_infrastructure", self.data.create_data_plan, "data", 60.0),
            ("model_configuration", self.model.create_model_plan, "modeling", 68.0),
            ("memory_architecture", self.memory.create_memory_architecture, "memory", 74.0),
            ("testing_report", self.testing.create_testing_report, "testing", 82.0),
            ("security_assessment", self.security.create_security_assessment, "security", 88.0),
            ("deployment_package", self.deployment.create_deployment_package, "deployment", 94.0),
            ("monitoring_dashboard", self.monitoring.create_monitoring_plan, "monitoring", 98.0),
            ("maintenance_guide", self.maintenance.create_maintenance_guide, "completed", 100.0),
        ]

        for output_type, action, status, completion in steps:
            artifact = action(project, output_dir)
            results[output_type] = artifact
            self.db.add_output(project_id, output_type, artifact.get("file_path", ""))
            self.db.update_status(project_id, status, completion)

        self.log(f"Automation execution completed for {company}")
        return results

    def _create_execution_plan(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "01_automation_execution_plan.md", "Automation Execution Plan", {
            "Objectives": [project.get("objectives", project.get("goals", "Reduce manual work and improve operational efficiency."))],
            "Delivery Strategy": ["Analyze requirements", "design architecture", "build workflows and AI systems", "validate", "secure", "deploy", "monitor."],
            "Team Allocation": ["Solution architect", "multi-agent engineer", "workflow engineer", "integration engineer", "testing", "security", "deployment", "monitoring."],
            "Success Metrics": ["Time saved", "error reduction", "revenue impact", "workflow completion rate", "user satisfaction."],
        })
