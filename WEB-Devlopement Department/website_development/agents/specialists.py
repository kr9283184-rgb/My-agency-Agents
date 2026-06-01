from website_development.agents.base_agent import BaseAgent


class BusinessAnalysisAgent(BaseAgent):
    def analyze(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "01_business_analysis_report.md", "Business Analysis Report", {
            "Business Model": ["Clarify revenue model, offer ladder, sales cycle, and trust signals."],
            "Audience": ["Define primary visitors, decision makers, objections, and conversion intent."],
            "Competitors": ["Review competitor positioning, navigation, offers, and conversion paths."],
            "User Journey": ["Map awareness, evaluation, conversion, and post-conversion states."],
        })


class ContentStructureAgent(BaseAgent):
    def create_architecture(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "02_content_architecture.md", "Content Architecture", {
            "Sitemap": ["Home", "Services", "About", "Case Studies", "Contact"],
            "Navigation": ["Keep primary navigation concise and action-focused."],
            "Heading Strategy": ["Use one clear H1 per page and descriptive H2 sections."],
        })


class UIUXDesignDirectorAgent(BaseAgent):
    def create_blueprint(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "03_ux_blueprint.md", "UX Blueprint", {
            "User Flows": ["Visitor lands, validates fit, reviews proof, chooses CTA, submits inquiry."],
            "Wireframes": ["Hero with direct offer", "Service proof section", "Conversion form", "FAQ"],
            "Accessibility": ["Keyboard-friendly controls", "Visible focus states", "Readable contrast"],
        })


class CreativeDesignAgent(BaseAgent):
    def create_design_system(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "04_visual_design_system.md", "Visual Design System", {
            "Color System": ["Primary brand color, neutral text scale, success/error states."],
            "Typography": ["Readable display heading, body font, consistent type scale."],
            "Components": ["Buttons", "Forms", "Cards", "Navigation", "Footer"],
        })


class LandingPageSpecialistAgent(BaseAgent):
    def create_blueprint(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "05_landing_page_blueprint.md", "Landing Page Blueprint", {
            "Offer": ["Lead with the client's strongest service promise."],
            "CTA": ["Use one primary conversion action per page."],
            "Conversion Blocks": ["Proof", "Benefits", "Process", "Risk reversal", "Form"],
        })


class FrontendDevelopmentAgent(BaseAgent):
    def generate_source(self, project: dict, output_dir: str) -> dict:
        project_dir = self._project_dir(project, output_dir)
        file_path = f"{project_dir}/06_frontend_source_code.md"
        company = project.get("company_name", "Client")
        with open(file_path, "w") as f:
            f.write(f"# Frontend Source Code Plan - {company}\n\n")
            f.write("## Recommended Stack\n\n")
            f.write("- Static HTML/CSS for simple brochure sites\n")
            f.write("- React or Next.js for interactive applications and portals\n")
            f.write("- Tailwind or design-system CSS for scalable UI implementation\n\n")
            f.write("## Starter Structure\n\n")
            f.write("```text\nsrc/\n  components/\n  pages/\n  styles/\n  lib/\n```\n")
        return {"file_path": file_path, "status": "created"}


class ShopifyDevelopmentAgent(BaseAgent):
    def create_package(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "07_shopify_store_package.md", "Shopify Store Package", {
            "Store Setup": ["Theme selection", "Product templates", "Collection structure"],
            "Checkout": ["Trust badges", "Cart clarity", "Post-purchase flow"],
        })


class WordPressDevelopmentAgent(BaseAgent):
    def create_package(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "08_wordpress_project_package.md", "WordPress Project Package", {
            "CMS Setup": ["Pages", "Menus", "Reusable blocks", "Editor roles"],
            "Plugins": ["SEO", "Forms", "Caching", "Security"],
        })


class SEOOptimizationAgent(BaseAgent):
    def optimize(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "09_seo_report.md", "SEO Report", {
            "Technical SEO": ["Clean URLs", "XML sitemap", "Robots rules", "Schema markup"],
            "On-Page SEO": ["Meta titles", "Meta descriptions", "Heading hierarchy"],
            "Local SEO": ["NAP consistency", "Location pages", "Review signals"],
        })


class PerformanceOptimizationAgent(BaseAgent):
    def optimize(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "10_performance_report.md", "Performance Report", {
            "Core Web Vitals": ["Optimize LCP assets", "Reduce layout shift", "Limit long tasks"],
            "Assets": ["Compress images", "Defer non-critical scripts", "Minify CSS"],
            "Caching": ["Static asset caching", "CDN deployment", "Server compression"],
        })


class WebsiteSecurityAgent(BaseAgent):
    def verify(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "11_security_report.md", "Security Report", {
            "Headers": ["Content-Security-Policy", "X-Frame-Options", "Referrer-Policy"],
            "Forms": ["Validate input", "Protect against spam", "Avoid exposing secrets"],
            "Authentication": ["Use secure sessions and least-privilege roles when portals are required."],
        })


class QATestingAgent(BaseAgent):
    def test(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "12_qa_approval_report.md", "QA Approval Report", {
            "Functional QA": ["Forms", "Navigation", "Links", "Interactive states"],
            "Responsive QA": ["Mobile", "Tablet", "Desktop"],
            "Browser QA": ["Chrome", "Safari", "Firefox", "Edge"],
        })


class DeploymentAgent(BaseAgent):
    def deploy(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "13_deployment_guide.md", "Deployment Guide", {
            "Targets": ["Vercel", "Netlify", "Cloudflare Pages", "Traditional hosting"],
            "Checklist": ["Environment variables", "DNS", "SSL", "Analytics", "Rollback plan"],
        })


class WebsiteMaintenanceAgent(BaseAgent):
    def create_guide(self, project: dict, output_dir: str) -> dict:
        return self._write_markdown(project, output_dir, "14_maintenance_guide.md", "Maintenance Guide", {
            "Monitoring": ["Uptime", "Performance", "SEO health", "Security updates"],
            "Cadence": ["Weekly health checks", "Monthly SEO review", "Quarterly UX review"],
        })
