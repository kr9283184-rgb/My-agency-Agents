from dataclasses import dataclass, field
from typing import Optional

from security_department.config import Config
from security_department.database import SecurityDatabase
from security_department.agents.chief_security_officer_agent import ChiefSecurityOfficerAgent


@dataclass
class SecurityResult:
    db: Optional[SecurityDatabase] = None
    total_assessments: int = 0
    completed: int = 0
    failed: int = 0
    reports: list = field(default_factory=list)

    def summary(self) -> dict:
        return {
            "total_assessments": self.total_assessments,
            "completed": self.completed,
            "failed": self.failed,
        }


class SecurityOrchestrator:
    def __init__(self, db: Optional[SecurityDatabase] = None):
        self.db = db or SecurityDatabase()
        self.cso = ChiefSecurityOfficerAgent(db=self.db)

    def run(self, assessment: Optional[dict] = None, output_dir: str = "") -> SecurityResult:
        result = SecurityResult(db=self.db)
        assessments = [assessment or self._default_assessment()]
        result.total_assessments = len(assessments)

        for item in assessments:
            try:
                outputs = self.cso.execute_assessment(item, output_dir or Config.OUTPUT_DIR)
                result.completed += 1
                result.reports.append({
                    "assessment_id": item.get("assessment_id", ""),
                    "target": item.get("target_name", ""),
                    "status": "completed",
                    "outputs": outputs,
                })
            except Exception as e:
                result.failed += 1
                result.reports.append({
                    "assessment_id": item.get("assessment_id", "") if item else "",
                    "target": item.get("target_name", "") if item else "",
                    "status": "failed",
                    "error": str(e),
                })
        return result

    def run_status(self, assessment_id: str = "") -> dict:
        if assessment_id:
            assessment = self.db.get_assessment(assessment_id)
            if not assessment:
                return {"error": f"Security assessment {assessment_id} not found"}
            return {
                "assessment": assessment,
                "outputs": self.db.get_outputs(assessment_id),
                "vulnerabilities": self.db.get_vulnerabilities(assessment_id),
            }
        return {
            "assessments": self.db.get_assessments(),
            "summary": self.db.summary(),
            "source_dbs": Config.source_db_status(),
        }

    def _default_assessment(self) -> dict:
        return {
            "assessment_id": "security-demo-001",
            "target_name": "Demo System",
            "target_type": "agency_operations",
            "assessment_type": Config.DEFAULT_ASSESSMENT_TYPE,
            "risk_level": Config.DEFAULT_RISK_LEVEL,
            "owner": "Security Team",
            "scope": "Agency websites, AI agents, APIs, databases, automations, dashboards, and operational workflows.",
        }
