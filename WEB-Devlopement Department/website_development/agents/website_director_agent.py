from website_development.agents.base_agent import BaseAgent
from website_development.agents.specialists import (
    BusinessAnalysisAgent,
    ContentStructureAgent,
    UIUXDesignDirectorAgent,
    CreativeDesignAgent,
    LandingPageSpecialistAgent,
    FrontendDevelopmentAgent,
    ShopifyDevelopmentAgent,
    WordPressDevelopmentAgent,
    SEOOptimizationAgent,
    PerformanceOptimizationAgent,
    WebsiteSecurityAgent,
    QATestingAgent,
    DeploymentAgent,
    WebsiteMaintenanceAgent,
)


class WebsiteDevelopmentDirectorAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.business = BusinessAnalysisAgent(db=self.db)
        self.content = ContentStructureAgent(db=self.db)
        self.ux = UIUXDesignDirectorAgent(db=self.db)
        self.creative = CreativeDesignAgent(db=self.db)
        self.landing = LandingPageSpecialistAgent(db=self.db)
        self.frontend = FrontendDevelopmentAgent(db=self.db)
        self.shopify = ShopifyDevelopmentAgent(db=self.db)
        self.wordpress = WordPressDevelopmentAgent(db=self.db)
        self.seo = SEOOptimizationAgent(db=self.db)
        self.performance = PerformanceOptimizationAgent(db=self.db)
        self.security = WebsiteSecurityAgent(db=self.db)
        self.qa = QATestingAgent(db=self.db)
        self.deployment = DeploymentAgent(db=self.db)
        self.maintenance = WebsiteMaintenanceAgent(db=self.db)

    def execute_project(self, project: dict, output_dir: str) -> dict:
        project_id = project.get("project_id", "")
        company = project.get("company_name", "Unknown")
        self.log(f"Starting website execution for {company} ({project_id})")

        self.db.add_project(project)
        self.db.update_status(project_id, "analysis", 5.0)

        steps = [
            ("business_analysis", self.business.analyze, "planning", 10.0),
            ("content_architecture", self.content.create_architecture, "ux", 18.0),
            ("ux_blueprint", self.ux.create_blueprint, "design", 25.0),
            ("design_system", self.creative.create_design_system, "design", 32.0),
            ("landing_page", self.landing.create_blueprint, "development", 40.0),
            ("frontend_source", self.frontend.generate_source, "development", 55.0),
            ("shopify_package", self.shopify.create_package, "cms", 62.0),
            ("wordpress_package", self.wordpress.create_package, "cms", 68.0),
            ("seo_report", self.seo.optimize, "optimization", 75.0),
            ("performance_report", self.performance.optimize, "optimization", 82.0),
            ("security_report", self.security.verify, "qa", 88.0),
            ("qa_report", self.qa.test, "deployment", 93.0),
            ("deployment_guide", self.deployment.deploy, "maintenance", 97.0),
            ("maintenance_guide", self.maintenance.create_guide, "completed", 100.0),
        ]

        results = {}
        for output_type, action, status, completion in steps:
            artifact = action(project, output_dir)
            results[output_type] = artifact
            self.db.add_output(project_id, output_type, artifact.get("file_path", ""))
            self.db.update_status(project_id, status, completion)

        self.log(f"Website execution completed for {company}")
        return results
