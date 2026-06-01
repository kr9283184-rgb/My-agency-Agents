from security_department.agents.base_agent import BaseAgent


class SecurityArchitectAgent(BaseAgent):
    def create_architecture_plan(self, assessment: dict, output_dir: str) -> dict:
        return self._write_markdown(assessment, output_dir, "02_security_architecture_plan.md", "Security Architecture Plan", {
            "Access Controls": ["Enforce least privilege, scoped service accounts, and documented approval for elevated access."],
            "Authentication": ["Use MFA for admin access, strong session controls, and secure credential storage."],
            "Authorization": ["Define role-based permissions for users, agents, automations, APIs, and dashboards."],
            "Segmentation": ["Separate public services, internal dashboards, databases, and privileged automation runners."],
        })


class ApplicationSecurityAgent(BaseAgent):
    def review_application(self, assessment: dict, output_dir: str) -> dict:
        return self._write_markdown(assessment, output_dir, "03_application_security_report.md", "Application Security Report", {
            "Input Validation": ["Validate request bodies, query parameters, file uploads, and webhook payloads."],
            "Authentication Flows": ["Review login, password reset, token rotation, session expiration, and admin paths."],
            "Authorization Checks": ["Verify object-level access control and tenant isolation on sensitive resources."],
            "Security Misconfiguration": ["Check debug flags, CORS policy, exposed stack traces, headers, and secret leakage."],
        })


class VulnerabilityManagementAgent(BaseAgent):
    def create_vulnerability_register(self, assessment: dict, output_dir: str) -> dict:
        assessment_id = assessment.get("assessment_id", "")
        baseline_items = [
            ("Dependency patch review required", "medium", "Run dependency audit and update outdated packages."),
            ("Secret handling review required", "high", "Move secrets to environment variables or a managed secret store."),
            ("Backup verification missing", "medium", "Schedule recovery tests and document restore procedure."),
        ]
        for title, severity, recommendation in baseline_items:
            self.db.add_vulnerability(assessment_id, title, severity, recommendation)

        return self._write_markdown(assessment, output_dir, "04_vulnerability_register.md", "Vulnerability Register", {
            "Prioritization": ["Critical issues require immediate containment and executive visibility.", "High issues should be fixed in the current sprint.", "Medium and low issues should enter the remediation backlog."],
            "Initial Register": [f"{severity.upper()}: {title} - {recommendation}" for title, severity, recommendation in baseline_items],
            "Remediation Tracking": ["Assign owner, due date, verification method, and evidence for each item."],
        })


class BugInvestigationAgent(BaseAgent):
    def create_bug_report(self, assessment: dict, output_dir: str) -> dict:
        return self._write_markdown(assessment, output_dir, "05_bug_resolution_report.md", "Bug Resolution Report", {
            "Investigation Scope": ["Review crashes, system errors, failed jobs, latency spikes, and workflow instability."],
            "Root Cause Analysis": ["Collect logs, identify triggering conditions, isolate affected services, and confirm reproduction steps."],
            "Recommended Fixes": ["Add regression tests, improve error handling, add monitoring, and document operational limits."],
        })


class ThreatDetectionAgent(BaseAgent):
    def create_threat_alert_report(self, assessment: dict, output_dir: str) -> dict:
        return self._write_markdown(assessment, output_dir, "06_threat_alert_report.md", "Threat Alert Report", {
            "Monitored Signals": ["Login failures", "API spikes", "unusual geolocation", "privileged actions", "agent tool usage anomalies."],
            "Detection Rules": ["Alert on repeated authentication failures, impossible travel, token misuse, and abnormal data export volume."],
            "Triage": ["Classify as benign, suspicious, confirmed incident, or false positive with documented evidence."],
        })


class AccessControlAgent(BaseAgent):
    def create_access_report(self, assessment: dict, output_dir: str) -> dict:
        return self._write_markdown(assessment, output_dir, "07_access_control_report.md", "Access Control Report", {
            "Role Review": ["Inventory admins, developers, operators, agents, service accounts, and client users."],
            "Least Privilege": ["Remove unused permissions and separate read, write, deploy, billing, and secret-management roles."],
            "Audit Cadence": ["Review privileged accounts monthly and all accounts quarterly."],
        })


class IncidentResponseAgent(BaseAgent):
    def create_incident_response_report(self, assessment: dict, output_dir: str) -> dict:
        return self._write_markdown(assessment, output_dir, "08_incident_response_report.md", "Incident Response Report", {
            "Response Workflow": ["Verify incident", "assess impact", "contain affected systems", "notify stakeholders", "recover", "document lessons learned."],
            "Containment": ["Rotate exposed credentials, disable compromised accounts, isolate affected services, preserve logs."],
            "Communications": ["Define internal owner, client contact, executive escalation, and regulatory notification path if applicable."],
        })


class NetworkSecurityAgent(BaseAgent):
    def create_network_assessment(self, assessment: dict, output_dir: str) -> dict:
        return self._write_markdown(assessment, output_dir, "09_network_security_assessment.md", "Network Security Assessment", {
            "Boundary Controls": ["Firewall rules, private database access, administrative IP restrictions, and secure ingress paths."],
            "Traffic Monitoring": ["Track unusual outbound traffic, exposed management ports, and unexpected service-to-service calls."],
            "Hardening": ["Disable unused services, require TLS, document allowed ports, and maintain infrastructure inventory."],
        })


class AISecurityAgent(BaseAgent):
    def create_ai_security_report(self, assessment: dict, output_dir: str) -> dict:
        return self._write_markdown(assessment, output_dir, "10_ai_security_report.md", "AI Security Report", {
            "Prompt Safety": ["Protect system prompts, validate tool inputs, and define clear refusal boundaries for unsafe requests."],
            "Data Leakage": ["Keep client data scoped by tenant, redact secrets from logs, and limit retrieval to approved knowledge bases."],
            "Tool Governance": ["Require allowlisted tools, parameter validation, audit logs, and human approval for sensitive actions."],
            "Automation Abuse": ["Monitor high-volume messaging, unexpected file access, abnormal API usage, and bypass attempts."],
        })


class BackupRecoveryAgent(BaseAgent):
    def create_recovery_readiness_report(self, assessment: dict, output_dir: str) -> dict:
        return self._write_markdown(assessment, output_dir, "11_recovery_readiness_report.md", "Recovery Readiness Report", {
            "Backups": ["Automate database and artifact backups with encryption and retention rules."],
            "Recovery Tests": ["Run periodic restore tests and record recovery time and recovery point results."],
            "Continuity": ["Document degraded-mode operations, manual workarounds, and critical vendor dependencies."],
        })


class ComplianceAgent(BaseAgent):
    def create_compliance_assessment(self, assessment: dict, output_dir: str) -> dict:
        return self._write_markdown(assessment, output_dir, "12_compliance_assessment.md", "Compliance Assessment", {
            "Policies": ["Document acceptable use, access control, incident response, backup, and data retention policies."],
            "Data Handling": ["Classify data, define retention, track consent, and limit access to business need."],
            "Evidence": ["Maintain audit logs, access reviews, vulnerability remediation records, and recovery test results."],
        })


class SecurityMonitoringAgent(BaseAgent):
    def create_monitoring_report(self, assessment: dict, output_dir: str) -> dict:
        return self._write_markdown(assessment, output_dir, "13_security_monitoring_report.md", "Security Monitoring Report", {
            "Daily Reporting": ["Security alerts", "bug reports", "system health", "failed jobs", "unusual user activity."],
            "Weekly Reporting": ["Risk assessment", "vulnerability summary", "security improvements", "incident trends."],
            "Monthly Reporting": ["Security score", "compliance status", "incident summary", "control maturity."],
        })


class ReliabilityAgent(BaseAgent):
    def create_reliability_report(self, assessment: dict, output_dir: str) -> dict:
        return self._write_markdown(assessment, output_dir, "14_system_reliability_report.md", "System Reliability Report", {
            "Availability": ["Define uptime target, dependency map, on-call ownership, and health checks."],
            "Integrity": ["Add data validation, transaction safety, idempotent jobs, and audit trails."],
            "Resilience": ["Use retries, circuit breakers, queue backpressure, graceful degradation, and runbooks."],
        })
