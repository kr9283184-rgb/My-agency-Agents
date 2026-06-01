from testing_department.agents.base_agent import BaseAgent


class RequirementValidationAgent(BaseAgent):
    def validate(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "02_requirement_validation_report.md", "Requirement Validation Report", {
            "Scope Completion": ["Verify all scoped features, integrations, pages, workflows, and AI behaviors are present."],
            "Requirement Coverage": [project.get("requirements", "Map every product requirement to at least one test case.")],
            "Acceptance Criteria": [project.get("acceptance_criteria", "Confirm measurable pass/fail criteria before release.")],
        })


class FunctionalTestingAgent(BaseAgent):
    def test(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "03_functional_testing_report.md", "Functional Testing Report", {
            "Features": ["Buttons", "forms", "navigation", "search", "checkout", "booking", "account flows", "admin workflows."],
            "Expected vs Actual": ["Record actual behavior, expected behavior, evidence, and pass/fail result per test case."],
            "Workflow Coverage": ["Validate happy path, error states, empty states, and permission-sensitive actions."],
        })


class WebsiteTestingAgent(BaseAgent):
    def test(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "04_website_testing_report.md", "Website Testing Report", {
            "Responsive Layouts": ["Desktop", "tablet", "mobile", "navigation menu", "content scaling", "forms."],
            "SEO Elements": ["Title tags", "meta descriptions", "headings", "schema", "image alt text", "canonical links."],
            "Conversion Flow": ["CTA visibility, contact forms, booking paths, confirmation messages, analytics events."],
        })


class AISystemTestingAgent(BaseAgent):
    def test(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "05_ai_quality_report.md", "AI Quality Report", {
            "Response Quality": ["Accuracy", "consistency", "tone", "policy adherence", "hallucination resistance."],
            "Prompt Accuracy": ["Validate task instructions, refusal boundaries, context handling, and escalation rules."],
            "Agent Systems": ["Memory behavior", "tool usage", "agent communication", "failure handling", "human handoff."],
        })


class AutomationTestingAgent(BaseAgent):
    def test(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "06_automation_testing_report.md", "Automation Testing Report", {
            "Workflow Triggers": ["Webhooks", "schedules", "form submissions", "CRM stage changes", "notification events."],
            "Integrations": ["CRM updates", "calendar booking", "email delivery", "WhatsApp messages", "database writes."],
            "End-to-End Validation": ["Confirm each workflow completes, logs outcome, retries safe failures, and alerts on blockers."],
        })


class APITestingAgent(BaseAgent):
    def test(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "07_api_testing_report.md", "API Testing Report", {
            "Endpoints": ["Validate methods, status codes, request schemas, response schemas, pagination, and filtering."],
            "Authentication": ["Verify invalid tokens, expired sessions, permission failures, and account separation."],
            "Error Handling": ["Confirm useful errors without exposing secrets, stack traces, or internal implementation details."],
        })


class PerformanceTestingAgent(BaseAgent):
    def test(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "08_performance_report.md", "Performance Report", {
            "Speed": ["Page load time", "API response time", "workflow execution duration", "AI response latency."],
            "Resource Usage": ["CPU", "memory", "database load", "queue depth", "model/API call volume."],
            "Scalability": ["Define load thresholds, bottlenecks, and acceptable degradation behavior."],
        })


class SecurityVerificationAgent(BaseAgent):
    def verify(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "09_security_verification_report.md", "Security Verification Report", {
            "Authentication": ["Login, session handling, password reset, MFA paths, token rotation."],
            "Authorization": ["Role permissions, object-level checks, tenant boundaries, admin-only actions."],
            "Data Protection": ["Secret exposure, sensitive logs, input validation, file upload controls, privacy boundaries."],
        })


class UserExperienceTestingAgent(BaseAgent):
    def evaluate(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "10_ux_evaluation_report.md", "UX Evaluation Report", {
            "Ease of Use": ["Clarity of labels, predictable navigation, low-friction workflows, helpful errors."],
            "Accessibility": ["Keyboard support", "focus states", "contrast", "screen-reader labels", "semantic structure."],
            "User Journey": ["Evaluate first impression, conversion path, task completion, and support/handoff flows."],
        })


class CrossPlatformTestingAgent(BaseAgent):
    def test(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "11_compatibility_report.md", "Compatibility Report", {
            "Browsers": ["Chrome", "Firefox", "Edge", "Safari"],
            "Devices": ["Desktop", "tablet", "mobile"],
            "Compatibility Risks": ["Layout shifts", "unsupported APIs", "touch interactions", "viewport overflow", "font rendering."],
        })


class BugTrackingAgent(BaseAgent):
    def create_bug_register(self, project: dict, output_dir: str) -> dict:
        qa_id = project.get("qa_id", "")
        baseline_bugs = [
            ("Missing evidence for full regression coverage", "medium", "Run saved regression checklist and attach proof."),
            ("Performance budget needs final confirmation", "low", "Measure final build under realistic network conditions."),
        ]
        for title, severity, steps in baseline_bugs:
            self.db.add_bug(qa_id, title, severity, steps, project.get("owner", ""))

        return self._write_markdown(project, output_dir, "12_bug_register.md", "Bug Register", {
            "Severity Levels": ["Critical", "High", "Medium", "Low"],
            "Initial Bugs": [f"{severity.upper()}: {title} - {steps}" for title, severity, steps in baseline_bugs],
            "Tracking Fields": ["Severity", "owner", "reproduction steps", "status", "expected fix version", "verification evidence."],
        })


class RegressionTestingAgent(BaseAgent):
    def test(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "13_regression_testing_report.md", "Regression Testing Report", {
            "Coverage": ["Previously working features", "recently changed areas", "shared components", "critical business flows."],
            "Verification": ["Confirm new changes did not break navigation, forms, workflows, integrations, or AI behavior."],
            "Automation Candidates": ["Promote repeatable smoke tests and critical-path checks to automated regression tests."],
        })


class ReleaseApprovalAgent(BaseAgent):
    def create_certificate(self, project: dict, output_dir: str, score: float, decision: str) -> dict:
        return self._write_markdown(project, output_dir, "14_release_approval_certificate.md", "Release Approval Certificate", {
            "Final Quality Score": [f"{score:.1f}"],
            "Release Recommendation": [decision],
            "Approval Rules": ["90-100 Excellent", "80-89 Good", "70-79 Acceptable", "Below 70 Failed"],
            "Known Issues": ["Review bug register before release and confirm no critical or high-severity blockers remain open."],
        })
