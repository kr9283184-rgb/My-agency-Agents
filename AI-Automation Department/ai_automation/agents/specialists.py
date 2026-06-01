from ai_automation.agents.base_agent import BaseAgent


class SolutionArchitectAgent(BaseAgent):
    def create_architecture(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "02_technical_architecture.md", "Technical Architecture Document", {
            "System Architecture": ["Define APIs, databases, model providers, workflow boundaries, and handoff points."],
            "Agent Architecture": ["Separate planner, executor, memory, validation, and reporting responsibilities."],
            "Integration Strategy": ["Map CRM, calendar, email, WhatsApp, database, and business app connections."],
            "Operational Constraints": [project.get("constraints", "Confirm rate limits, data access, privacy, and deployment limits.")],
        })


class MultiAgentSystemEngineer(BaseAgent):
    def build_system_plan(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "03_multi_agent_system.md", "Multi-Agent System Package", {
            "Framework Recommendation": ["Use LangGraph for stateful workflows or CrewAI for role-based collaborative execution."],
            "Agent Team": ["Coordinator", "Tool Executor", "Research Agent", "Validation Agent", "Reporting Agent"],
            "State Design": ["Project context", "task queue", "tool outputs", "approval state", "error history"],
        })


class WorkflowAutomationEngineer(BaseAgent):
    def create_workflows(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "04_workflow_package.md", "Automation Workflow Package", {
            "n8n Workflows": ["Lead intake", "CRM update", "email notification", "report generation", "human approval branch"],
            "Triggers": ["Webhook", "schedule", "form submission", "CRM stage change"],
            "Failure Handling": ["Retry transient errors", "send alert on permanent failure", "log failed payloads."],
        })


class ChatbotEngineerAgent(BaseAgent):
    def build_chatbot_plan(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "05_chatbot_system.md", "Production Chatbot System", {
            "Bot Capabilities": ["FAQ responses", "lead qualification", "context-aware recommendations", "human handoff"],
            "Conversation Memory": ["Session state for current chat and long-term profile memory for known customers."],
            "Guardrails": ["Business-hours handoff", "disallowed advice boundaries", "confidence-based escalation."],
        })


class ReceptionistEngineerAgent(BaseAgent):
    def build_receptionist_plan(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "06_ai_receptionist_system.md", "AI Receptionist System", {
            "Voice Flow": ["Greeting", "intent detection", "lead qualification", "calendar booking", "CRM update"],
            "Voice Stack": ["Whisper or Vosk for speech-to-text", "Piper for text-to-speech"],
            "Escalation": ["Transfer urgent calls and low-confidence conversations to a human operator."],
        })


class IntegrationEngineerAgent(BaseAgent):
    def create_integration_package(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "07_integration_package.md", "Integration Package", {
            "Systems": ["CRM", "calendar", "email", "WhatsApp", "website forms", "analytics"],
            "Authentication": ["Use environment variables, scoped API keys, and least-privilege service accounts."],
            "Sync Rules": ["Define source of truth, conflict handling, retry policy, and audit logging."],
        })


class DataEngineerAgent(BaseAgent):
    def create_data_plan(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "08_data_infrastructure.md", "Data Infrastructure", {
            "Databases": ["PostgreSQL or Supabase for structured records", "ChromaDB for retrieval memory when needed."],
            "Pipelines": ["Normalize inbound events, deduplicate records, persist status changes, archive raw payloads."],
            "Data Quality": ["Required fields", "validation rules", "duplicate checks", "retention policy."],
        })


class AIModelEngineerAgent(BaseAgent):
    def create_model_plan(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "09_model_configuration.md", "Model Configuration Plan", {
            "Reasoning Models": ["Qwen or DeepSeek for complex planning and workflow decisions."],
            "Coding Models": ["DeepSeek or Qwen coding models for implementation support."],
            "Fallbacks": ["Llama or Mistral for local/offline operation where cost or privacy matters."],
            "Optimization": ["Route simple tasks to smaller models and reserve strong models for critical decisions."],
        })


class MemorySystemEngineerAgent(BaseAgent):
    def create_memory_architecture(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "10_memory_architecture.md", "Memory Architecture", {
            "Session Memory": ["Track active conversation state, current objective, recent tool calls, and unresolved tasks."],
            "Long-Term Memory": ["Store customer profile, preferences, prior outcomes, and approved knowledge."],
            "Retrieval": ["Use sentence-transformer embeddings and scoped vector collections per client or project."],
        })


class TestingValidationAgent(BaseAgent):
    def create_testing_report(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "11_testing_report.md", "Testing Report", {
            "Accuracy": ["Golden test conversations", "expected classification outcomes", "response-quality checks."],
            "Reliability": ["Workflow retries", "integration failure simulations", "load-sensitive paths."],
            "Acceptance Criteria": ["Automation completes core jobs, logs failures, and supports human override."],
        })


class SecurityComplianceAgent(BaseAgent):
    def create_security_assessment(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "12_security_assessment.md", "Security Assessment", {
            "Data Handling": ["Minimize sensitive data collection and define retention/deletion policies."],
            "Access Control": ["Role-based access, scoped credentials, audit logs, encrypted secrets."],
            "Privacy": ["Document consent requirements, customer data sources, and human handoff boundaries."],
        })


class DeploymentEngineerAgent(BaseAgent):
    def create_deployment_package(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "13_deployment_package.md", "Deployment Package", {
            "Targets": ["Docker", "VPS", "cloud app platform", "local server for privacy-sensitive deployments."],
            "Environment": ["Model endpoints", "database URLs", "API keys", "webhook URLs", "monitoring credentials."],
            "Release Plan": ["Staging validation", "production rollout", "rollback path", "post-launch smoke tests."],
        })


class MonitoringAgent(BaseAgent):
    def create_monitoring_plan(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "14_monitoring_dashboard.md", "Monitoring Dashboard Plan", {
            "Health Metrics": ["Uptime", "workflow success rate", "latency", "model errors", "integration failures."],
            "Business Metrics": ["Hours saved", "leads processed", "appointments booked", "support tickets resolved."],
            "Reports": ["Daily engineering report", "weekly performance report", "maintenance report."],
        })


class MaintenanceAgent(BaseAgent):
    def create_maintenance_guide(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "15_maintenance_guide.md", "Maintenance Guide", {
            "Cadence": ["Daily error review", "weekly workflow review", "monthly model and prompt optimization."],
            "Runbooks": ["Credential rotation", "webhook failure recovery", "database backup restore", "human escalation."],
            "Continuous Improvement": ["Track automation ROI and prioritize fixes by client impact."],
        })
