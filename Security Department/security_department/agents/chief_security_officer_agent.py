from security_department.agents.base_agent import BaseAgent
from security_department.agents.specialists import (
    SecurityArchitectAgent,
    ApplicationSecurityAgent,
    VulnerabilityManagementAgent,
    BugInvestigationAgent,
    ThreatDetectionAgent,
    AccessControlAgent,
    IncidentResponseAgent,
    NetworkSecurityAgent,
    AISecurityAgent,
    BackupRecoveryAgent,
    ComplianceAgent,
    SecurityMonitoringAgent,
    ReliabilityAgent,
)


class ChiefSecurityOfficerAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.architect = SecurityArchitectAgent(db=self.db)
        self.appsec = ApplicationSecurityAgent(db=self.db)
        self.vulnerability = VulnerabilityManagementAgent(db=self.db)
        self.bug = BugInvestigationAgent(db=self.db)
        self.threat = ThreatDetectionAgent(db=self.db)
        self.access = AccessControlAgent(db=self.db)
        self.incident = IncidentResponseAgent(db=self.db)
        self.network = NetworkSecurityAgent(db=self.db)
        self.ai_security = AISecurityAgent(db=self.db)
        self.recovery = BackupRecoveryAgent(db=self.db)
        self.compliance = ComplianceAgent(db=self.db)
        self.monitoring = SecurityMonitoringAgent(db=self.db)
        self.reliability = ReliabilityAgent(db=self.db)

    def execute_assessment(self, assessment: dict, output_dir: str) -> dict:
        assessment_id = assessment.get("assessment_id", "")
        target = assessment.get("target_name", "Unknown")
        self.log(f"Starting security assessment for {target} ({assessment_id})")

        self.db.add_assessment(assessment)
        self.db.update_status(assessment_id, "executive_review", 5.0)

        results = {
            "executive_summary": self._create_executive_summary(assessment, output_dir)
        }
        self.db.add_output(assessment_id, "executive_summary", results["executive_summary"].get("file_path", ""))

        steps = [
            ("security_architecture", self.architect.create_architecture_plan, "architecture", 12.0),
            ("application_security", self.appsec.review_application, "application_review", 20.0),
            ("vulnerability_register", self.vulnerability.create_vulnerability_register, "vulnerability_review", 30.0),
            ("bug_resolution", self.bug.create_bug_report, "bug_investigation", 38.0),
            ("threat_alerts", self.threat.create_threat_alert_report, "threat_detection", 46.0),
            ("access_control", self.access.create_access_report, "access_review", 54.0),
            ("incident_response", self.incident.create_incident_response_report, "incident_response", 62.0),
            ("network_security", self.network.create_network_assessment, "network_review", 70.0),
            ("ai_security", self.ai_security.create_ai_security_report, "ai_security", 78.0),
            ("recovery_readiness", self.recovery.create_recovery_readiness_report, "recovery", 84.0),
            ("compliance_assessment", self.compliance.create_compliance_assessment, "compliance", 90.0),
            ("security_monitoring", self.monitoring.create_monitoring_report, "monitoring", 96.0),
            ("system_reliability", self.reliability.create_reliability_report, "completed", 100.0),
        ]

        for output_type, action, status, completion in steps:
            artifact = action(assessment, output_dir)
            results[output_type] = artifact
            self.db.add_output(assessment_id, output_type, artifact.get("file_path", ""))
            self.db.update_status(assessment_id, status, completion, self._security_score(assessment))

        self.log(f"Security assessment completed for {target}")
        return results

    def _create_executive_summary(self, assessment: dict, output_dir: str) -> dict:
        return self._write_markdown(assessment, output_dir, "01_executive_security_summary.md", "Executive Security Summary", {
            "Mission": ["Protect availability, integrity, confidentiality, and reliability across agency and client systems."],
            "Assessment Scope": [assessment.get("scope", "Websites, APIs, databases, AI agents, automations, dashboards, and operational processes.")],
            "Top Priorities": ["Resolve critical vulnerabilities quickly", "strengthen access control", "verify backups", "monitor suspicious activity", "document incident response."],
            "Success Criteria": ["Systems remain secure", "downtime is minimized", "unauthorized access is detected", "incidents are handled effectively."],
        })

    def _security_score(self, assessment: dict) -> float:
        risk = assessment.get("risk_level", "medium").lower()
        return {
            "low": 88.0,
            "medium": 78.0,
            "high": 66.0,
            "critical": 52.0,
        }.get(risk, 78.0)
