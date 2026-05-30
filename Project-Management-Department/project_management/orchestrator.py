from dataclasses import dataclass, field
from typing import Optional
from project_management.database import ProjectDatabase
from project_management.agents.project_director_agent import ProjectDirectorAgent


@dataclass
class ProjectResult:
    db: Optional[ProjectDatabase] = None
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


class ProjectOrchestrator:
    def __init__(self, db: Optional[ProjectDatabase] = None):
        self.db = db or ProjectDatabase()
        self.director = ProjectDirectorAgent(db=self.db)

    def run(self, project_id: str = "", output_dir: str = "", change_request: Optional[dict] = None) -> ProjectResult:
        result = ProjectResult(db=self.db)

        if project_id:
            projects = [self._fetch_project_from_db(project_id)]
            projects = [p for p in projects if p]
        else:
            projects = self._get_projects_to_manage()

        if not projects:
            self._log("No projects found to manage")
            return result

        result.total_projects = len(projects)

        for i, project in enumerate(projects, 1):
            company = project.get("company_name", "Unknown")
            pid = project.get("project_id", project.get("lead_id", ""))
            project["project_id"] = pid
            self._log(f"\n{'='*60}")
            self._log(f"[{i}/{len(projects)}] Managing project: {company} ({pid})")
            self._log(f"{'='*60}")

            try:
                if change_request:
                    cr_result = self.director.change_agent.process_change_request(
                        project, change_request, output_dir
                    )
                    result.executed += 1
                    result.reports.append({
                        "project_id": pid,
                        "company": company,
                        "status": "change_request_created",
                        "outputs": {"change_request": cr_result},
                    })
                    self._log(f"✓ Change request processed for {company}")
                else:
                    execution_result = self.director.execute_project(project, output_dir)
                    result.executed += 1
                    result.reports.append({
                        "project_id": pid,
                        "company": company,
                        "status": "completed",
                        "outputs": execution_result,
                    })
                    self._log(f"✓ Project {company} executed successfully")

            except Exception as e:
                self._log(f"✗ Failed to execute project {company}: {e}")
                result.failed += 1
                result.reports.append({
                    "project_id": pid,
                    "company": company,
                    "status": "failed",
                    "error": str(e),
                })

        self._log(f"\n{'='*60}")
        self._log(f"PROJECT MANAGEMENT COMPLETE — {result.executed}/{result.total_projects} executed")
        self._log(f"{'='*60}")

        return result

    def run_status(self, project_id: str = "") -> dict:
        if project_id:
            project = self.db.get_project(project_id)
            if not project:
                return {"error": f"Project {project_id} not found"}
            tasks = self.db.get_tasks(project_id)
            milestones = self.db.get_milestones(project_id)
            risks = self.db.get_risks(project_id, "open")
            budget = self.db.get_budget_summary(project_id)

            completed_tasks = sum(1 for t in tasks if t["state"] == "completed")
            total_tasks = len(tasks)

            return {
                "project": {
                    "project_id": project["project_id"],
                    "company": project["company_name"],
                    "status": project["status"],
                    "completion_pct": project["completion_pct"],
                    "tasks_completed": f"{completed_tasks}/{total_tasks}",
                    "open_risks": len(risks),
                    "budget_health": budget["budget_health"],
                    "profit_margin": f"{budget['profit_margin_pct']:.1f}%",
                }
            }
        else:
            projects = self.db.get_projects()
            status_list = []
            for p in projects:
                tasks = self.db.get_tasks(p["project_id"])
                completed = sum(1 for t in tasks if t["state"] == "completed")
                total = len(tasks)
                risks = self.db.get_risks(p["project_id"], "open")
                status_list.append({
                    "project_id": p["project_id"],
                    "company": p["company_name"],
                    "status": p["status"],
                    "completion_pct": p["completion_pct"],
                    "tasks": f"{completed}/{total}",
                    "risks": len(risks),
                })

            return {
                "projects": status_list,
                "summary": self.db.project_summary(),
                "portfolio": self.db.portfolio_health(),
            }

    def run_weekly_report(self, project_id: str = "", output_dir: str = "") -> dict:
        if project_id:
            project = self.db.get_project(project_id)
            if project:
                return self.director.progress_agent.track_progress(
                    project, output_dir, "weekly"
                )
        return {"error": "Project not found"}

    def run_monthly_executive(self, output_dir: str = "") -> dict:
        projects = self.db.get_projects()
        reports = []
        for p in projects:
            report = self.director.progress_agent.track_progress(p, output_dir, "monthly")
            reports.append(report)
        return {
            "portfolio_health": self.db.portfolio_health(),
            "project_summary": self.db.project_summary(),
            "reports": reports,
        }

    def process_change_request(self, project_id: str, cr_data: dict, output_dir: str = "") -> dict:
        project = self.db.get_project(project_id)
        if not project:
            return {"error": f"Project {project_id} not found"}
        return self.director.change_agent.process_change_request(project, cr_data, output_dir)

    def _get_projects_to_manage(self) -> list:
        from project_management.config import Config
        projects = self.db.get_projects()
        if projects:
            return projects
        onboarding = self.db.get_completed_onboarding_projects()
        if onboarding:
            return [self._convert_onboarding_to_project(o) for o in onboarding]
        return []

    def _fetch_project_from_db(self, project_id: str) -> Optional[dict]:
        project = self.db.get_project(project_id)
        if project:
            return project
        onboarding = self.db.get_completed_onboarding_projects()
        for o in onboarding:
            if o.get("lead_id") == project_id or o.get("company_name", "").lower().replace(" ", "_") == project_id.lower().replace(" ", "_"):
                return self._convert_onboarding_to_project(o)
        return None

    def _convert_onboarding_to_project(self, onboarding: dict) -> dict:
        import uuid
        outputs = self.db.get_onboarding_outputs(onboarding.get("lead_id", ""))
        handover_file = next(
            (o["file_path"] for o in outputs if "handover" in o.get("output_type", "")),
            ""
        )
        return {
            "project_id": str(uuid.uuid4())[:8],
            "lead_id": onboarding.get("lead_id", ""),
            "company_name": onboarding.get("company_name", ""),
            "contact_name": onboarding.get("contact_name", ""),
            "email": onboarding.get("email", ""),
            "whatsapp_phone": onboarding.get("whatsapp_phone", ""),
            "industry": onboarding.get("industry", ""),
            "proposal_type": onboarding.get("proposal_type", "service"),
            "deal_amount": onboarding.get("deal_amount", 0.0),
            "status": "planning",
            "priority": "medium",
            "onboarding_handover_file": handover_file,
        }

    def _log(self, message: str):
        print(message)
