import os
from datetime import datetime, timedelta
from typing import Optional
from project_management.agents.base_agent import BaseAgent


class PlanningAgent(BaseAgent):
    MASTER_PHASES = {
        "website": [
            {"phase": 1, "title": "Discovery & Research", "weeks": 2},
            {"phase": 2, "title": "Design & Prototyping", "weeks": 2},
            {"phase": 3, "title": "Development", "weeks": 4},
            {"phase": 4, "title": "Testing & QA", "weeks": 1},
            {"phase": 5, "title": "Launch & Deploy", "weeks": 1},
        ],
        "automation": [
            {"phase": 1, "title": "Process Discovery", "weeks": 2},
            {"phase": 2, "title": "Solution Design", "weeks": 2},
            {"phase": 3, "title": "Development & Integration", "weeks": 4},
            {"phase": 4, "title": "Testing & Validation", "weeks": 1},
            {"phase": 5, "title": "Deployment & Training", "weeks": 1},
        ],
        "seo": [
            {"phase": 1, "title": "Audit & Research", "weeks": 1},
            {"phase": 2, "title": "On-Page Optimization", "weeks": 3},
            {"phase": 3, "title": "Content Strategy", "weeks": 3},
            {"phase": 4, "title": "Link Building & Outreach", "weeks": 4},
            {"phase": 5, "title": "Reporting & Monitoring", "weeks": 1},
        ],
    }

    DEFAULT_PHASES = [
        {"phase": 1, "title": "Discovery & Research", "weeks": 2},
        {"phase": 2, "title": "Planning & Design", "weeks": 2},
        {"phase": 3, "title": "Execution", "weeks": 4},
        {"phase": 4, "title": "Testing & QA", "weeks": 1},
        {"phase": 5, "title": "Launch & Handover", "weeks": 1},
    ]

    def create_project_plan(self, project: dict, output_dir: str = "") -> dict:
        project_id = project.get("project_id", "")
        company = project.get("company_name", "")
        proposal_type = project.get("proposal_type", "service")
        deal_amount = project.get("deal_amount", 0)

        phases = self.MASTER_PHASES.get(proposal_type, self.DEFAULT_PHASES)

        start_date = datetime.now()
        milestones = []
        cumulative_weeks = 0

        for phase_info in phases:
            cumulative_weeks += phase_info["weeks"]
            due_date = start_date + timedelta(weeks=cumulative_weeks)
            milestone = {
                "project_id": project_id,
                "title": phase_info["title"],
                "phase": phase_info["phase"],
                "due_date": due_date.strftime("%Y-%m-%d"),
                "status": "pending",
                "completion_pct": 0.0,
                "deliverables": self._get_phase_deliverables(proposal_type, phase_info["phase"]),
                "dependencies": self._get_phase_dependencies(phase_info["phase"]),
            }
            mid = self.db.add_milestone(milestone)
            milestone["milestone_id"] = mid
            milestones.append(milestone)

        tasks = self._generate_sprint_tasks(project_id, proposal_type, phases, milestones)
        for task in tasks:
            self.db.add_task(task)

        file_path = ""
        if output_dir:
            company_dir = os.path.join(output_dir, company.replace(" ", "_"))
            os.makedirs(company_dir, exist_ok=True)
            file_path = os.path.join(company_dir, "01_master_project_plan.md")
            with open(file_path, "w") as f:
                self._write_plan(f, project, phases, milestones, tasks)

        total_weeks = sum(p["weeks"] for p in phases)
        target_end = (start_date + timedelta(weeks=total_weeks)).strftime("%Y-%m-%d")
        self.db.update_project(project_id, {
            "target_end_date": target_end,
        })

        self.log(f"Project plan created for {company} — {len(milestones)} milestones, {len(tasks)} tasks")

        return {
            "file_path": file_path,
            "milestones": milestones,
            "tasks_count": len(tasks),
            "total_weeks": total_weeks,
            "target_end_date": target_end,
            "phases": phases,
        }

    def _get_phase_deliverables(self, proposal_type: str, phase: int) -> str:
        deliverables_map = {
            (1, "website"): "Project brief, sitemap, competitor analysis",
            (2, "website"): "Wireframes, mockups, design prototypes",
            (3, "website"): "Functional website, responsive implementation, CMS setup",
            (4, "website"): "QA report, bug fixes, performance optimizations",
            (5, "website"): "Live website, handover documentation, training",
            (1, "automation"): "Process maps, requirements doc, data flow diagrams",
            (2, "automation"): "Solution architecture, technical specifications",
            (3, "automation"): "Automated workflows, integrations, API connections",
            (4, "automation"): "Test results, validation report, UAT sign-off",
            (5, "automation"): "Deployed solution, runbook, team training",
        }
        return deliverables_map.get((phase, proposal_type), "Phase deliverables")

    def _get_phase_dependencies(self, phase: int) -> str:
        deps = {
            1: "Project kickoff approved",
            2: "Phase 1 completed",
            3: "Phase 2 completed",
            4: "Phase 3 completed",
            5: "Phase 4 completed, QA approved",
        }
        return deps.get(phase, "")

    def _generate_sprint_tasks(self, project_id: str, proposal_type: str, phases: list, milestones: list) -> list:
        tasks = []
        task_templates = {
            "website": {
                1: [
                    ("Kickoff meeting", "Schedule and conduct project kickoff", "project_manager", 4, "high"),
                    ("Requirements finalization", "Finalize and document all requirements", "pm_team", 8, "high"),
                    ("Competitor research", "Research competitor websites and features", "design_team", 6, "medium"),
                    ("Sitemap creation", "Create site architecture and sitemap", "design_team", 4, "high"),
                ],
                2: [
                    ("Wireframe design", "Design wireframes for all pages", "design_team", 16, "high"),
                    ("Visual mockup creation", "Create high-fidelity visual mockups", "design_team", 20, "high"),
                    ("Client design review", "Present designs for client feedback", "project_manager", 4, "high"),
                    ("Design revisions", "Implement client feedback on designs", "design_team", 8, "medium"),
                ],
                3: [
                    ("Frontend development", "Build frontend components and pages", "dev_team", 40, "high"),
                    ("Backend development", "Implement backend functionality", "dev_team", 32, "high"),
                    ("CMS integration", "Set up and configure CMS", "dev_team", 8, "medium"),
                    ("Responsive testing", "Test all pages across devices", "dev_team", 8, "medium"),
                ],
                4: [
                    ("Functional testing", "Test all features and functionality", "qa_team", 16, "high"),
                    ("Performance optimization", "Optimize loading speed and performance", "dev_team", 8, "medium"),
                    ("Bug fixes", "Fix all identified bugs", "dev_team", 12, "high"),
                    ("Client UAT", "Client user acceptance testing", "project_manager", 4, "high"),
                ],
                5: [
                    ("Deployment preparation", "Prepare deployment checklist and backup", "dev_team", 4, "high"),
                    ("Production deployment", "Deploy to production environment", "dev_team", 4, "high"),
                    ("Final walkthrough", "Conduct final walkthrough with client", "project_manager", 2, "high"),
                    ("Handover documentation", "Prepare and deliver handover docs", "project_manager", 4, "medium"),
                ],
            },
            "automation": {
                1: [
                    ("Kickoff meeting", "Schedule and conduct project kickoff", "project_manager", 4, "high"),
                    ("Process mapping", "Map current business processes", "automation_team", 12, "high"),
                    ("Requirements workshop", "Conduct requirements gathering workshop", "automation_team", 8, "high"),
                    ("Technical feasibility", "Assess technical feasibility of automation", "automation_team", 6, "medium"),
                ],
                2: [
                    ("Solution architecture", "Design automation solution architecture", "automation_team", 16, "high"),
                    ("Technical spec", "Write detailed technical specifications", "automation_team", 12, "high"),
                    ("Integration design", "Design integration points and APIs", "automation_team", 8, "medium"),
                    ("Client approval", "Get client approval on solution design", "project_manager", 4, "high"),
                ],
                3: [
                    ("Workflow development", "Build automation workflows", "automation_team", 40, "high"),
                    ("API integration", "Implement API integrations", "automation_team", 16, "high"),
                    ("Database setup", "Set up database schemas and connections", "automation_team", 8, "medium"),
                    ("Error handling", "Implement error handling and logging", "automation_team", 8, "medium"),
                ],
                4: [
                    ("Unit testing", "Test individual automation components", "qa_team", 16, "high"),
                    ("Integration testing", "Test end-to-end integration", "qa_team", 12, "high"),
                    ("Performance testing", "Test automation performance and reliability", "qa_team", 8, "medium"),
                    ("UAT", "Client user acceptance testing", "project_manager", 4, "high"),
                ],
                5: [
                    ("Production deployment", "Deploy automation to production", "automation_team", 8, "high"),
                    ("Team training", "Train client team on automation usage", "automation_team", 8, "high"),
                    ("Documentation", "Create user and admin documentation", "automation_team", 6, "medium"),
                    ("Handover", "Final handover and project closure", "project_manager", 4, "high"),
                ],
            },
        }

        templates = task_templates.get(proposal_type, task_templates.get("website", {}))
        for milestone in milestones:
            phase_num = milestone["phase"]
            phase_tasks = templates.get(phase_num, [])
            for t_title, t_desc, t_owner, t_hours, t_priority in phase_tasks:
                tasks.append({
                    "project_id": project_id,
                    "milestone_id": milestone.get("milestone_id", 0),
                    "title": t_title,
                    "description": t_desc,
                    "owner": t_owner,
                    "priority": t_priority,
                    "state": "pending",
                    "estimated_hours": t_hours,
                })
        return tasks

    def _write_plan(self, f, project: dict, phases: list, milestones: list, tasks: list):
        company = project.get("company_name", "")
        proposal_type = project.get("proposal_type", "service")
        deal_amount = project.get("deal_amount", 0)

        f.write(f"# Master Project Plan — {company}\n\n")
        f.write("---\n\n")

        f.write("## 1. Project Overview\n\n")
        f.write(f"- **Company:** {company}\n")
        f.write(f"- **Project Type:** {proposal_type}\n")
        f.write(f"- **Deal Value:** ${float(deal_amount):,.2f}\n")
        f.write(f"- **Total Duration:** {sum(p['weeks'] for p in phases)} weeks\n")
        f.write(f"- **Status:** Planning\n\n")

        f.write("---\n\n")

        f.write("## 2. Project Roadmap\n\n")
        f.write("| Phase | Title | Duration | Deliverables |\n")
        f.write("|-------|-------|----------|--------------|\n")
        for p in phases:
            f.write(f"| {p['phase']} | {p['title']} | {p['weeks']} weeks | {self._get_phase_deliverables(proposal_type, p['phase'])} |\n")
        f.write("\n")

        f.write("---\n\n")

        f.write("## 3. Milestones\n\n")
        f.write("| # | Milestone | Due Date | Status |\n")
        f.write("|---|-----------|----------|--------|\n")
        for m in milestones:
            f.write(f"| {m['phase']} | {m['title']} | {m.get('due_date', 'TBD')} | {m['status']} |\n")
        f.write("\n")

        f.write("---\n\n")

        f.write("## 4. Work Breakdown Structure\n\n")
        current_phase = 0
        for task in tasks:
            phase_num = task.get("milestone_id", 0)
            if phase_num != current_phase:
                phase_title = next((p["title"] for p in phases if p["phase"] == phase_num), f"Phase {phase_num}")
                if current_phase > 0:
                    f.write("\n")
                f.write(f"### Phase {phase_num}: {phase_title}\n\n")
                current_phase = phase_num
            f.write(f"- [ ] **{task['title']}** — {task['description']} ({task['estimated_hours']}h, {task['priority']})\n")
        f.write("\n")

        f.write("---\n\n")

        f.write("## 5. Dependencies\n\n")
        f.write("| Phase | Depends On |\n")
        f.write("|-------|------------|\n")
        for p in phases:
            deps = self._get_phase_dependencies(p["phase"])
            f.write(f"| {p['title']} | {deps} |\n")
        f.write("\n")

        f.write("---\n\n")

        f.write("## 6. Sprint Plan\n\n")
        f.write("Sprints are 2-week iterations within each phase.\n\n")
        total_sprints = sum(p["weeks"] for p in phases) // 2
        for sprint_num in range(1, total_sprints + 1):
            f.write(f"### Sprint {sprint_num}\n")
            f.write(f"- Duration: 2 weeks\n")
            f.write(f"- Goals: TBD during sprint planning\n")
            f.write(f"- Reviews: End of sprint\n\n")
