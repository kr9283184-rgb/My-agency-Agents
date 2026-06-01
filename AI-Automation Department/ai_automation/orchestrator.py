from dataclasses import dataclass, field
from typing import Optional

from ai_automation.config import Config
from ai_automation.database import AutomationDatabase
from ai_automation.agents.automation_director_agent import AutomationDirectorAgent


@dataclass
class AutomationResult:
    db: Optional[AutomationDatabase] = None
    total_projects: int = 0
    executed: int = 0
    failed: int = 0
    reports: list = field(default_factory=list)

    def summary(self) -> dict:
        return {
            "total_projects": self.total_projects,
            "executed": self.executed,
            "failed": self.failed,
        }


class AutomationOrchestrator:
    def __init__(self, db: Optional[AutomationDatabase] = None):
        self.db = db or AutomationDatabase()
        self.director = AutomationDirectorAgent(db=self.db)

    def run(self, project: Optional[dict] = None, output_dir: str = "") -> AutomationResult:
        result = AutomationResult(db=self.db)
        projects = [project or self._default_project()]
        result.total_projects = len(projects)

        for item in projects:
            try:
                outputs = self.director.execute_project(item, output_dir or Config.OUTPUT_DIR)
                result.executed += 1
                result.reports.append({
                    "project_id": item.get("project_id", ""),
                    "company": item.get("company_name", ""),
                    "status": "completed",
                    "outputs": outputs,
                })
            except Exception as e:
                result.failed += 1
                result.reports.append({
                    "project_id": item.get("project_id", "") if item else "",
                    "company": item.get("company_name", "") if item else "",
                    "status": "failed",
                    "error": str(e),
                })
        return result

    def run_status(self, project_id: str = "") -> dict:
        if project_id:
            project = self.db.get_project(project_id)
            if not project:
                return {"error": f"Automation project {project_id} not found"}
            return {
                "project": project,
                "outputs": self.db.get_outputs(project_id),
            }
        return {
            "projects": self.db.get_projects(),
            "summary": self.db.summary(),
        }

    def _default_project(self) -> dict:
        return {
            "project_id": "automation-demo-001",
            "company_name": "Demo Client",
            "client_name": "",
            "industry": "professional services",
            "project_type": Config.DEFAULT_PROJECT_TYPE,
            "priority": "medium",
            "stack": Config.DEFAULT_STACK,
            "objectives": "Reduce manual work, improve response speed, and automate repeatable operations.",
        }
