import os
from datetime import datetime, timedelta
from typing import Optional
from project_management.agents.base_agent import BaseAgent


class ResourceAllocationAgent(BaseAgent):
    DEPARTMENTS = [
        "Website & Design Department",
        "AI Automation Department",
        "QR-Based_Restaurant-Ordering-System Team",
        "QA Department",
    ]

    ROLE_MAP = {
        "website": {
            "department": "Website & Design Department",
            "roles": ["Project Manager", "UI/UX Designer", "Frontend Developer", "Backend Developer"],
        },
        "automation": {
            "department": "AI Automation Department",
            "roles": ["Project Manager", "Automation Engineer", "Integration Specialist", "Data Analyst"],
        },
        "qr_ordering": {
            "department": "QR-Based_Restaurant-Ordering-System Team",
            "roles": ["Project Manager", "Full Stack Developer", "Mobile Developer", "QA Engineer"],
        },
        "seo": {
            "department": "Website & Design Department",
            "roles": ["Project Manager", "SEO Specialist", "Content Writer", "Analytics Specialist"],
        },
    }

    DEFAULT_ALLOCATION = {
        "website": [
            ("Project Manager", 50),
            ("UI/UX Designer", 100),
            ("Frontend Developer", 100),
            ("Backend Developer", 100),
        ],
        "automation": [
            ("Project Manager", 50),
            ("Automation Engineer", 100),
            ("Integration Specialist", 75),
            ("Data Analyst", 25),
        ],
        "qr_ordering": [
            ("Project Manager", 50),
            ("Full Stack Developer", 100),
            ("Mobile Developer", 100),
            ("QA Engineer", 50),
        ],
        "seo": [
            ("Project Manager", 25),
            ("SEO Specialist", 100),
            ("Content Writer", 50),
            ("Analytics Specialist", 25),
        ],
    }

    def allocate_resources(self, project: dict, output_dir: str = "") -> dict:
        project_id = project.get("project_id", "")
        company = project.get("company_name", "")
        proposal_type = project.get("proposal_type", "service")

        dept_info = self.ROLE_MAP.get(proposal_type, self.ROLE_MAP["website"])
        department = dept_info["department"]
        allocations = self.DEFAULT_ALLOCATION.get(proposal_type, self.DEFAULT_ALLOCATION["website"])

        self.db.update_project(project_id, {"assigned_team": department})

        resources = []
        for role_name, allocation_pct in allocations:
            resource = {
                "project_id": project_id,
                "department": department,
                "role": role_name,
                "member_name": "",
                "allocation_pct": allocation_pct,
                "start_date": datetime.now().strftime("%Y-%m-%d"),
                "status": "assigned",
            }
            rid = self.db.add_resource(resource)
            resource["resource_id"] = rid
            resources.append(resource)

        qa_resource = {
            "project_id": project_id,
            "department": "QA Department",
            "role": "QA Engineer",
            "member_name": "",
            "allocation_pct": 50,
            "start_date": (datetime.now() + timedelta(weeks=6)).strftime("%Y-%m-%d"),
            "status": "scheduled",
        }
        qid = self.db.add_resource(qa_resource)
        qa_resource["resource_id"] = qid
        resources.append(qa_resource)

        file_path = ""
        if output_dir:
            company_dir = os.path.join(output_dir, company.replace(" ", "_"))
            os.makedirs(company_dir, exist_ok=True)
            file_path = os.path.join(company_dir, "02_resource_assignment_report.md")
            with open(file_path, "w") as f:
                self._write_report(f, project, department, resources)

        self.log(f"Resources allocated for {company} — {len(resources)} team members across {department} and QA")

        return {
            "file_path": file_path,
            "department": department,
            "resources": resources,
            "total_resources": len(resources),
        }

    def _write_report(self, f, project: dict, department: str, resources: list):
        company = project.get("company_name", "")
        proposal_type = project.get("proposal_type", "")

        f.write(f"# Resource Assignment Report — {company}\n\n")
        f.write("---\n\n")

        f.write("## 1. Assigned Department\n\n")
        f.write(f"**Primary Department:** {department}\n")
        f.write(f"**Project Type:** {proposal_type}\n\n")

        f.write("---\n\n")

        f.write("## 2. Team Allocation\n\n")
        f.write("| Role | Department | Allocation | Status |\n")
        f.write("|------|------------|------------|--------|\n")
        for r in resources:
            f.write(f"| {r['role']} | {r['department']} | {r['allocation_pct']}% | {r['status']} |\n")
        f.write("\n")

        f.write("---\n\n")

        f.write("## 3. Capacity Summary\n\n")
        total_allocation = sum(r["allocation_pct"] for r in resources)
        f.write(f"- **Total Team Members:** {len(resources)}\n")
        f.write(f"- **Total Allocation:** {total_allocation}%\n")
        f.write(f"- **Average Allocation:** {total_allocation // len(resources) if resources else 0}%\n")
        f.write(f"- **QA Scheduled:** Yes (weeks 5+)\n\n")

        f.write("---\n\n")

        f.write("## 4. Utilization Notes\n\n")
        f.write("- Project Manager is shared across multiple projects (50% allocation)\n")
        f.write("- QA team joins during testing phase (typically weeks 5-8)\n")
        f.write("- Additional resources can be added if scope increases\n")
        f.write("- Weekly capacity reviews scheduled\n")
