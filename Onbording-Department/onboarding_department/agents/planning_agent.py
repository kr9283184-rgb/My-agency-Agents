import os
from typing import Optional
from onboarding_department.agents.base_agent import BaseAgent


class PlanningAgent(BaseAgent):
    def create_roadmap(self, lead: dict, scope_details: Optional[dict] = None, output_dir: str = "") -> dict:
        company = lead.get("company_name", "")
        contact = lead.get("contact_name", "")
        proposal_type = lead.get("proposal_type", "service")

        phases = self._generate_phases(proposal_type)

        file_path = ""
        if output_dir:
            company_dir = os.path.join(output_dir, company.replace(" ", "_"))
            os.makedirs(company_dir, exist_ok=True)
            file_path = os.path.join(company_dir, "09_project_roadmap.md")
            with open(file_path, "w") as f:
                self._write_roadmap(f, company, contact, proposal_type, phases)
            self.log(f"Project roadmap saved to {file_path}")

        return {"file_path": file_path, "phases": phases}

    def _generate_phases(self, proposal_type: str) -> list:
        return [
            {
                "phase": 1,
                "name": "Research & Discovery",
                "duration": "Weeks 1-2",
                "tasks": self._get_phase_tasks(proposal_type, 1),
                "deliverables": ["Requirements document", "Brand analysis report", "Project scope"],
            },
            {
                "phase": 2,
                "name": "Design",
                "duration": "Weeks 3-4",
                "tasks": self._get_phase_tasks(proposal_type, 2),
                "deliverables": ["Wireframes", "Design mockups", "Design approval"],
            },
            {
                "phase": 3,
                "name": "Development",
                "duration": "Weeks 5-8",
                "tasks": self._get_phase_tasks(proposal_type, 3),
                "deliverables": ["Functional website/app", "Integration complete", "Development sign-off"],
            },
            {
                "phase": 4,
                "name": "Testing & QA",
                "duration": "Week 9",
                "tasks": self._get_phase_tasks(proposal_type, 4),
                "deliverables": ["QA report", "Bug fixes", "User acceptance testing"],
            },
            {
                "phase": 5,
                "name": "Launch",
                "duration": "Week 10",
                "tasks": self._get_phase_tasks(proposal_type, 5),
                "deliverables": ["Live deployment", "Launch documentation", "Handover complete"],
            },
        ]

    def _get_phase_tasks(self, proposal_type: str, phase: int) -> list:
        tasks = {
            1: {
                "website": [
                    "Client kickoff meeting",
                    "Review brand guidelines and assets",
                    "Competitor analysis",
                    "Sitemap and user flow creation",
                    "Technical requirements gathering",
                ],
                "automation": [
                    "Client kickoff meeting",
                    "Current workflow audit",
                    "Tool and system inventory",
                    "Automation opportunity identification",
                    "Technical feasibility assessment",
                ],
            },
            2: {
                "website": [
                    "Homepage design concepts",
                    "Inner page designs",
                    "Responsive design adaptation",
                    "Client review and feedback",
                    "Design iteration and approval",
                ],
                "automation": [
                    "Workflow diagram creation",
                    "Automation logic design",
                    "System architecture documentation",
                    "Integration design",
                    "Design review and approval",
                ],
            },
            3: {
                "website": [
                    "Front-end development",
                    "CMS integration",
                    "Content population",
                    "Responsive testing",
                    "Performance optimization",
                ],
                "automation": [
                    "Script and workflow development",
                    "API integrations",
                    "Database setup",
                    "Version control setup",
                    "Development testing",
                ],
            },
            4: {
                "website": [
                    "Cross-browser testing",
                    "Mobile device testing",
                    "Load time optimization",
                    "Form and function testing",
                    "Content and link verification",
                ],
                "automation": [
                    "Unit testing",
                    "Integration testing",
                    "User acceptance testing",
                    "Performance validation",
                    "Documentation review",
                ],
            },
            5: {
                "website": [
                    "Domain and DNS configuration",
                    "SSL certificate installation",
                    "Final content review",
                    "Production deployment",
                    "Post-launch monitoring",
                ],
                "automation": [
                    "Production deployment",
                    "Monitoring setup",
                    "Team training session",
                    "Documentation handover",
                    "Post-launch support",
                ],
            },
        }

        phase_tasks = tasks.get(phase, {})
        return phase_tasks.get(proposal_type, phase_tasks.get("website", [
            f"Phase {phase} task 1",
            f"Phase {phase} task 2",
            f"Phase {phase} task 3",
        ]))

    def _write_roadmap(self, f, company: str, contact: str, proposal_type: str, phases: list):
        f.write(f"# Project Roadmap — {company}\n\n")
        f.write(f"**Client:** {contact}\n")
        f.write(f"**Company:** {company}\n")
        f.write(f"**Project Type:** {proposal_type}\n")
        f.write(f"**Estimated Timeline:** 10 Weeks\n\n")
        f.write("---\n\n")

        f.write("## Project Timeline Overview\n\n")
        for ph in phases:
            bar_len = int(ph["phase"] * 4)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            f.write(f"**Phase {ph['phase']}: {ph['name']}** ({ph['duration']})\n")
            f.write(f"`{bar}`\n\n")

        f.write("---\n\n")

        for ph in phases:
            f.write(f"## Phase {ph['phase']}: {ph['name']}\n\n")
            f.write(f"**Duration:** {ph['duration']}\n\n")
            f.write("### Tasks\n\n")
            for i, task in enumerate(ph["tasks"], 1):
                f.write(f"{i}. {task}\n")
            f.write("\n")
            f.write("### Deliverables\n\n")
            for d in ph["deliverables"]:
                f.write(f"- {d}\n")
            f.write("\n---\n\n")

        f.write("## Key Milestones\n\n")
        f.write("| Date | Milestone |\n")
        f.write("|------|-----------|\n")
        f.write("| Week 1 | Project Kickoff |\n")
        f.write("| Week 2 | Requirements Finalized |\n")
        f.write("| Week 4 | Design Approved |\n")
        f.write("| Week 8 | Development Complete |\n")
        f.write("| Week 9 | QA Complete |\n")
        f.write("| Week 10 | Launch 🚀 |\n")
