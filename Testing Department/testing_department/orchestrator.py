from dataclasses import dataclass, field
from typing import Optional

from testing_department.config import Config
from testing_department.database import TestingDatabase
from testing_department.agents.qa_director_agent import QADirectorAgent


@dataclass
class TestingResult:
    db: Optional[TestingDatabase] = None
    total_projects: int = 0
    completed: int = 0
    failed: int = 0
    reports: list = field(default_factory=list)

    def summary(self) -> dict:
        return {
            "total_projects": self.total_projects,
            "completed": self.completed,
            "failed": self.failed,
        }


class TestingOrchestrator:
    __test__ = False

    def __init__(self, db: Optional[TestingDatabase] = None):
        self.db = db or TestingDatabase()
        self.director = QADirectorAgent(db=self.db)

    def run(self, project: Optional[dict] = None, output_dir: str = "") -> TestingResult:
        result = TestingResult(db=self.db)
        projects = [project or self._default_project()]
        result.total_projects = len(projects)

        for item in projects:
            try:
                outputs = self.director.execute_qa(item, output_dir or Config.OUTPUT_DIR)
                result.completed += 1
                result.reports.append({
                    "qa_id": item.get("qa_id", ""),
                    "product": item.get("product_name", ""),
                    "status": "completed",
                    "outputs": outputs,
                })
            except Exception as e:
                result.failed += 1
                result.reports.append({
                    "qa_id": item.get("qa_id", "") if item else "",
                    "product": item.get("product_name", "") if item else "",
                    "status": "failed",
                    "error": str(e),
                })
        return result

    def run_status(self, qa_id: str = "") -> dict:
        if qa_id:
            project = self.db.get_project(qa_id)
            if not project:
                return {"error": f"QA project {qa_id} not found"}
            return {
                "project": project,
                "outputs": self.db.get_outputs(qa_id),
                "bugs": self.db.get_bugs(qa_id),
            }
        return {
            "projects": self.db.get_projects(),
            "summary": self.db.summary(),
            "source_dbs": Config.source_db_status(),
        }

    def _default_project(self) -> dict:
        return {
            "qa_id": "qa-demo-001",
            "product_name": "Demo Product",
            "product_type": Config.DEFAULT_PRODUCT_TYPE,
            "owner": "QA Team",
            "risk_level": Config.DEFAULT_RISK_LEVEL,
            "requirements": "Validate product quality before client delivery.",
            "acceptance_criteria": "All critical paths pass and no critical bugs remain open.",
        }
