from dataclasses import dataclass, field
from typing import Optional

from website_development.config import Config
from website_development.database import WebsiteDatabase
from website_development.agents.website_director_agent import WebsiteDevelopmentDirectorAgent


@dataclass
class WebsiteResult:
    db: Optional[WebsiteDatabase] = None
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


class WebsiteOrchestrator:
    def __init__(self, db: Optional[WebsiteDatabase] = None):
        self.db = db or WebsiteDatabase()
        self.director = WebsiteDevelopmentDirectorAgent(db=self.db)

    def run(self, project: Optional[dict] = None, output_dir: str = "") -> WebsiteResult:
        result = WebsiteResult(db=self.db)
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
                return {"error": f"Website project {project_id} not found"}
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
            "project_id": "website-demo-001",
            "company_name": "Demo Client",
            "client_name": "",
            "industry": "professional services",
            "project_type": Config.DEFAULT_PROJECT_TYPE,
            "platform": Config.DEFAULT_PLATFORM,
            "goals": "Generate qualified inquiries and improve brand trust.",
        }
