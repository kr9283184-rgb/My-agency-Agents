import os
from typing import Optional
from onboarding_department.agents.base_agent import BaseAgent


class ScopeAgent(BaseAgent):
    def define_scope(self, lead: dict, requirements: Optional[dict] = None, output_dir: str = "") -> dict:
        company = lead.get("company_name", "")
        contact = lead.get("contact_name", "")
        proposal_type = requirements.get("project_type", "") if requirements else lead.get("proposal_type", "service")

        details = self._generate_scope(company, proposal_type)

        file_path = ""
        if output_dir:
            company_dir = os.path.join(output_dir, company.replace(" ", "_"))
            os.makedirs(company_dir, exist_ok=True)
            file_path = os.path.join(company_dir, "07_project_scope_document.md")
            with open(file_path, "w") as f:
                self._write_scope(f, company, contact, proposal_type, details)
            self.log(f"Project scope document saved to {file_path}")

        return {"file_path": file_path, "details": details}

    def _generate_scope(self, company: str, proposal_type: str) -> dict:
        return {
            "project_type": proposal_type,
            "included_features": self._get_included_features(proposal_type),
            "excluded_features": self._get_excluded_features(proposal_type),
            "deliverables": self._get_deliverables(proposal_type),
            "milestones": self._get_milestones(),
            "risks": self._get_risks(),
        }

    def _get_included_features(self, proposal_type: str) -> list:
        base = ["Project management and communication", "Quality assurance testing"]
        features = {
            "website": [
                "Custom website design (up to 5 pages)",
                "Responsive mobile design",
                "Contact form integration",
                "Basic SEO setup",
                "Google Analytics integration",
                "Social media links integration",
                "SSL certificate setup",
                "Domain and hosting configuration",
            ],
            "automation": [
                "Workflow analysis and documentation",
                "Custom automation script development",
                "Integration with existing tools",
                "Testing and validation",
                "Documentation and training",
                "30-day support period",
            ],
            "seo": [
                "Keyword research and analysis",
                "On-page SEO optimization",
                "Technical SEO audit",
                "Content recommendations",
                "Monthly performance reports",
                "Backlink analysis",
            ],
        }
        return base + features.get(proposal_type, ["Full-service engagement deliverables"])

    def _get_excluded_features(self, proposal_type: str) -> list:
        base = ["Content creation (unless specified)", "Paid advertising campaigns"]
        exclusions = {
            "website": [
                "E-commerce functionality",
                "Custom plugin development",
                "Third-party API integrations beyond 2",
                "Ongoing maintenance (available separately)",
                "Logo or brand identity design",
            ],
            "automation": [
                "Hardware procurement",
                "Legacy system migration",
                "Ongoing support beyond 30 days",
                "Staff training beyond 2 sessions",
            ],
            "seo": [
                "Content writing (available as add-on)",
                "Paid search management",
                "Social media management",
                "Guaranteed rankings",
            ],
        }
        return base + exclusions.get(proposal_type, ["Additional services available as add-ons"])

    def _get_deliverables(self, proposal_type: str) -> list:
        deliverables = {
            "website": [
                "Fully responsive website",
                "Source code and assets",
                "Admin documentation",
                "Launch checklist",
            ],
            "automation": [
                "Automation scripts and workflows",
                "Technical documentation",
                "User guide",
                "Test results report",
            ],
            "seo": [
                "SEO audit report",
                "Keyword research document",
                "Optimization implementation report",
                "Monthly performance dashboard",
            ],
        }
        return deliverables.get(proposal_type, [
            "Project deliverable package",
            "Documentation",
            "Training materials",
        ])

    def _get_milestones(self) -> list:
        return [
            {"milestone": "Project Kickoff", "week": 1, "description": "Introduction meeting, access setup, initial asset collection"},
            {"milestone": "Research Complete", "week": 2, "description": "Requirements finalized, brand analysis complete"},
            {"milestone": "Design Approval", "week": 4, "description": "Design concepts presented and approved"},
            {"milestone": "Development Complete", "week": 8, "description": "All development work finished"},
            {"milestone": "Testing Complete", "week": 9, "description": "QA testing passed, revisions done"},
            {"milestone": "Launch", "week": 10, "description": "Project goes live"},
        ]

    def _get_risks(self) -> list:
        return [
            {"risk": "Delayed asset delivery", "impact": "Medium", "mitigation": "Clear deadlines and reminders"},
            {"risk": "Scope creep", "impact": "High", "mitigation": "Regular scope reviews and change request process"},
            {"risk": "Client availability", "impact": "Medium", "mitigation": "Scheduled check-ins and async communication"},
            {"risk": "Technical compatibility", "impact": "Low", "mitigation": "Technical discovery phase upfront"},
        ]

    def _write_scope(self, f, company: str, contact: str, proposal_type: str, details: dict):
        f.write(f"# Project Scope Document — {company}\n\n")
        f.write(f"**Client:** {contact}\n")
        f.write(f"**Company:** {company}\n")
        f.write(f"**Project Type:** {proposal_type}\n\n")
        f.write("---\n\n")

        f.write("## Included Features\n\n")
        for feat in details.get("included_features", []):
            f.write(f"- [x] {feat}\n")
        f.write("\n")

        f.write("## Excluded Features\n\n")
        for feat in details.get("excluded_features", []):
            f.write(f"- [ ] {feat}\n")
        f.write("\n")

        f.write("## Deliverables\n\n")
        for d in details.get("deliverables", []):
            f.write(f"- {d}\n")
        f.write("\n")

        f.write("## Timeline & Milestones\n\n")
        f.write("| Milestone | Week | Description |\n")
        f.write("|-----------|------|-------------|\n")
        for m in details.get("milestones", []):
            f.write(f"| {m['milestone']} | {m['week']} | {m['description']} |\n")
        f.write("\n")

        f.write("## Risk Assessment\n\n")
        f.write("| Risk | Impact | Mitigation |\n")
        f.write("|------|--------|------------|\n")
        for r in details.get("risks", []):
            f.write(f"| {r['risk']} | {r['impact']} | {r['mitigation']} |\n")
        f.write("\n")

        f.write("---\n\n")
        f.write("## Change Request Process\n\n")
        f.write("Any changes to the scope will require a formal change request:\n")
        f.write("1. Submit change request describing the proposed change\n")
        f.write("2. Team assesses impact on timeline and budget\n")
        f.write("3. Client approves or rejects the change\n")
        f.write("4. Approved changes are incorporated into the project plan\n")
