import os
from typing import Optional
from onboarding_department.agents.base_agent import BaseAgent


class RequirementAgent(BaseAgent):
    def collect_requirements(self, lead: dict, proposal: Optional[dict] = None, output_dir: str = "") -> dict:
        company = lead.get("company_name", "")
        industry = lead.get("industry", "")
        contact = lead.get("contact_name", "")
        proposal_type = (proposal or {}).get("proposal_type", "service")

        details = self._generate_requirements(company, industry, contact, proposal_type)

        file_path = ""
        if output_dir:
            company_dir = os.path.join(output_dir, company.replace(" ", "_"))
            os.makedirs(company_dir, exist_ok=True)
            file_path = os.path.join(company_dir, "02_client_requirement_document.md")
            with open(file_path, "w") as f:
                f.write(f"# Client Requirement Document — {company}\n\n")
                f.write(f"**Company:** {company}\n")
                f.write(f"**Industry:** {industry}\n")
                f.write(f"**Contact:** {contact}\n")
                f.write(f"**Project Type:** {proposal_type}\n\n")
                f.write("---\n\n")
                self._write_website_requirements(f, details)

            self.log(f"Requirements document saved to {file_path}")

        return {
            "file_path": file_path,
            "details": details,
        }

    def _generate_requirements(self, company: str, industry: str, contact: str, proposal_type: str) -> dict:
        base = {
            "company_name": company,
            "industry": industry,
            "contact_name": contact,
            "project_type": proposal_type,
            "business_goals": self._get_default_goals(proposal_type),
            "target_audience": self._get_default_audience(industry),
            "competitors": [],
            "preferred_style": "professional and modern",
        }

        if proposal_type == "website":
            base.update({
                "required_pages": ["Home", "About", "Services", "Contact"],
                "website_goals": "Establish online presence and generate leads",
                "design_preferences": "Modern, clean, professional",
            })
        elif proposal_type == "automation":
            base.update({
                "current_workflow": "Manual processes",
                "pain_points": "Time-consuming repetitive tasks",
                "tools_used": [],
                "automation_goals": "Streamline operations and reduce manual work",
                "expected_outcomes": "Increased efficiency and reduced errors",
            })
        elif proposal_type == "seo":
            base.update({
                "current_ranking": "Not ranked for target keywords",
                "target_keywords": [],
                "seo_goals": "Improve search engine visibility",
                "competitor_websites": [],
            })
        else:
            base.update({
                "service_goals": "Improve business operations",
                "scope_description": "Full-service engagement",
            })

        return base

    def _get_default_goals(self, proposal_type: str) -> list:
        goals = {
            "website": ["Establish online presence", "Generate leads", "Showcase portfolio"],
            "automation": ["Reduce manual work", "Improve accuracy", "Save time"],
            "seo": ["Increase organic traffic", "Improve rankings", "Build authority"],
        }
        return goals.get(proposal_type, ["Improve business operations", "Increase efficiency"])

    def _get_default_audience(self, industry: str) -> str:
        audiences = {
            "real estate": "Home buyers, sellers, and investors",
            "healthcare": "Patients, medical professionals, healthcare providers",
            "technology": "Tech professionals, decision makers, IT managers",
            "education": "Students, educators, institutions",
            "ecommerce": "Online shoppers, retail customers",
        }
        return audiences.get(industry.lower(), "General public and industry professionals")

    def _write_website_requirements(self, f, details: dict):
        f.write("## Business Information\n\n")
        f.write(f"- **Company:** {details.get('company_name', '')}\n")
        f.write(f"- **Industry:** {details.get('industry', '')}\n")
        f.write(f"- **Contact:** {details.get('contact_name', '')}\n")
        f.write(f"- **Project Type:** {details.get('project_type', '')}\n\n")

        f.write("## Business Goals\n\n")
        for goal in details.get("business_goals", []):
            f.write(f"- {goal}\n")
        f.write("\n")

        f.write("## Target Audience\n\n")
        f.write(f"{details.get('target_audience', '')}\n\n")

        f.write("## Style Preferences\n\n")
        f.write(f"{details.get('preferred_style', '')}\n\n")

        if "required_pages" in details:
            f.write("## Required Pages\n\n")
            for page in details["required_pages"]:
                f.write(f"- {page}\n")
            f.write("\n")

        if "website_goals" in details:
            f.write("## Website Goals\n\n")
            f.write(f"{details['website_goals']}\n\n")

        if "current_workflow" in details:
            f.write("## Current Workflow\n\n")
            f.write(f"{details['current_workflow']}\n\n")
            f.write("## Pain Points\n\n")
            f.write(f"{details['pain_points']}\n\n")
            f.write("## Automation Goals\n\n")
            f.write(f"{details['automation_goals']}\n\n")
            f.write("## Expected Outcomes\n\n")
            f.write(f"{details['expected_outcomes']}\n\n")
