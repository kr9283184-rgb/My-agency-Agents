from testing_department.agents.base_agent import BaseAgent
from testing_department.agents.specialists import (
    RequirementValidationAgent,
    FunctionalTestingAgent,
    WebsiteTestingAgent,
    AISystemTestingAgent,
    AutomationTestingAgent,
    APITestingAgent,
    PerformanceTestingAgent,
    SecurityVerificationAgent,
    UserExperienceTestingAgent,
    CrossPlatformTestingAgent,
    BugTrackingAgent,
    RegressionTestingAgent,
    ReleaseApprovalAgent,
)


class QADirectorAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.requirements = RequirementValidationAgent(db=self.db)
        self.functional = FunctionalTestingAgent(db=self.db)
        self.website = WebsiteTestingAgent(db=self.db)
        self.ai_system = AISystemTestingAgent(db=self.db)
        self.automation = AutomationTestingAgent(db=self.db)
        self.api = APITestingAgent(db=self.db)
        self.performance = PerformanceTestingAgent(db=self.db)
        self.security = SecurityVerificationAgent(db=self.db)
        self.ux = UserExperienceTestingAgent(db=self.db)
        self.compatibility = CrossPlatformTestingAgent(db=self.db)
        self.bugs = BugTrackingAgent(db=self.db)
        self.regression = RegressionTestingAgent(db=self.db)
        self.release = ReleaseApprovalAgent(db=self.db)

    def execute_qa(self, project: dict, output_dir: str) -> dict:
        qa_id = project.get("qa_id", "")
        product = project.get("product_name", "Unknown")
        self.log(f"Starting QA review for {product} ({qa_id})")

        self.db.add_project(project)
        self.db.update_status(qa_id, "qa_planning", 5.0)

        score = self._quality_score(project)
        decision = self._qa_decision(score)
        results = {
            "final_qa_decision": self._create_final_qa_decision(project, output_dir, score, decision)
        }
        self.db.add_output(qa_id, "final_qa_decision", results["final_qa_decision"].get("file_path", ""))

        steps = [
            ("requirement_validation", self.requirements.validate, "requirement_validation", 12.0),
            ("functional_testing", self.functional.test, "functional_testing", 20.0),
            ("website_testing", self.website.test, "website_testing", 28.0),
            ("ai_quality", self.ai_system.test, "ai_testing", 36.0),
            ("automation_testing", self.automation.test, "automation_testing", 44.0),
            ("api_testing", self.api.test, "api_testing", 52.0),
            ("performance_testing", self.performance.test, "performance_testing", 60.0),
            ("security_verification", self.security.verify, "security_verification", 68.0),
            ("ux_evaluation", self.ux.evaluate, "ux_testing", 76.0),
            ("compatibility_testing", self.compatibility.test, "compatibility_testing", 84.0),
            ("bug_register", self.bugs.create_bug_register, "bug_tracking", 90.0),
            ("regression_testing", self.regression.test, "regression_testing", 96.0),
        ]

        for output_type, action, status, completion in steps:
            artifact = action(project, output_dir)
            results[output_type] = artifact
            self.db.add_output(qa_id, output_type, artifact.get("file_path", ""))
            self.db.update_status(qa_id, status, completion, score, decision)

        certificate = self.release.create_certificate(project, output_dir, score, decision)
        results["release_approval"] = certificate
        self.db.add_output(qa_id, "release_approval", certificate.get("file_path", ""))
        self.db.update_status(qa_id, "completed", 100.0, score, decision)

        self.log(f"QA review completed for {product}: {decision}")
        return results

    def _create_final_qa_decision(self, project: dict, output_dir: str, score: float, decision: str) -> dict:
        return self._write_markdown(project, output_dir, "01_final_qa_decision.md", "Final QA Decision", {
            "Decision": [decision],
            "Quality Score": [f"{score:.1f}"],
            "Gatekeeper Policy": ["No product should be released without QA approval and documented known issues."],
            "Score Model": ["Requirements 20%", "functionality 25%", "performance 15%", "security 15%", "UX 15%", "reliability 10%."],
        })

    def _quality_score(self, project: dict) -> float:
        risk = project.get("risk_level", "medium").lower()
        base = {
            "low": 92.0,
            "medium": 84.0,
            "high": 76.0,
            "critical": 62.0,
        }.get(risk, 84.0)
        if project.get("acceptance_criteria"):
            base += 2.0
        if project.get("requirements"):
            base += 2.0
        return min(base, 100.0)

    def _qa_decision(self, score: float) -> str:
        if score >= 90:
            return "Pass"
        if score >= 70:
            return "Pass With Issues"
        return "Fail"
