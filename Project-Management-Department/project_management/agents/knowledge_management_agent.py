import os
from datetime import datetime
from typing import Optional
from project_management.agents.base_agent import BaseAgent


class KnowledgeManagementAgent(BaseAgent):
    def capture_lessons(self, project: dict, output_dir: str = "") -> dict:
        project_id = project.get("project_id", "")
        company = project.get("company_name", "")

        lessons = self._generate_initial_lessons(project)
        for lesson in lessons:
            lesson["project_id"] = project_id
            self.db.add_lesson(lesson)

        all_lessons = self.db.get_lessons(project_id)
        best_practices = self.db.get_best_practices()

        file_path = ""
        if output_dir:
            company_dir = os.path.join(output_dir, company.replace(" ", "_"))
            os.makedirs(company_dir, exist_ok=True)
            file_path = os.path.join(company_dir, "12_knowledge_base_update.md")
            with open(file_path, "w") as f:
                self._write_update(f, project, all_lessons, best_practices)

        self.log(f"Knowledge base updated for {company} — {len(lessons)} lessons captured, {len(best_practices)} best practices")

        return {
            "file_path": file_path,
            "lessons": all_lessons,
            "best_practices": best_practices,
            "total_lessons": len(all_lessons),
        }

    def _generate_initial_lessons(self, project: dict) -> list:
        proposal_type = project.get("proposal_type", "service")
        deal_amount = project.get("deal_amount", 0)

        lessons = [
            {
                "category": "process",
                "title": "Project kickoff checklist effectiveness",
                "description": "Standard kickoff process was followed including requirements, assets, and scope definition",
                "impact": "Reduced ambiguity and aligned expectations from day one",
                "recommendation": "Continue using structured kickoff checklist for all projects",
                "is_best_practice": True,
                "tags": "kickoff, process, best-practice",
            },
            {
                "category": "communication",
                "title": "Weekly update cadence",
                "description": "Regular weekly updates kept client informed and reduced status-check interruptions",
                "impact": "Improved client satisfaction and reduced ad-hoc communication",
                "recommendation": "Maintain weekly update schedule; increase to bi-weekly for longer projects",
                "is_best_practice": True,
                "tags": "communication, reporting, client-satisfaction",
            },
        ]

        if deal_amount < 5000:
            lessons.append({
                "category": "budget",
                "title": "Small project budget management",
                "description": f"Project with ${deal_amount:,.0f} budget required careful scope management to maintain profitability",
                "impact": "Tight budgets limit flexibility for changes and revisions",
                "recommendation": "Include buffer for smaller projects; clearly communicate revision limits in SOW",
                "is_best_practice": True,
                "tags": "budget, scope, small-project",
            })

        if proposal_type == "automation":
            lessons.append({
                "category": "technical",
                "title": "Automation project discovery phase",
                "description": "Thorough process discovery was critical for accurate automation design",
                "impact": "Early discovery prevented rework during development",
                "recommendation": "Always include at least 2 weeks for process discovery in automation projects",
                "is_best_practice": True,
                "tags": "automation, discovery, requirements",
            })
        elif proposal_type == "website":
            lessons.append({
                "category": "technical",
                "title": "Website design approval process",
                "description": "Client design review phase identified the need for structured feedback cycles",
                "impact": "Limited revision rounds prevented scope creep in design phase",
                "recommendation": "Include maximum 2 revision rounds in SOW; additional rounds billed separately",
                "is_best_practice": True,
                "tags": "design, revisions, scope",
            })

        return lessons

    def add_lesson(self, project_id: str, category: str, title: str, description: str,
                   impact: str, recommendation: str, is_best_practice: bool = False, tags: str = "") -> int:
        lesson_id = self.db.add_lesson({
            "project_id": project_id,
            "category": category,
            "title": title,
            "description": description,
            "impact": impact,
            "recommendation": recommendation,
            "is_best_practice": is_best_practice,
            "tags": tags,
        })
        self.log(f"Lesson captured: {title}")
        return lesson_id

    def _write_update(self, f, project: dict, lessons: list, best_practices: list):
        company = project.get("company_name", "")

        f.write(f"# Knowledge Base Update — {company}\n\n")
        f.write("---\n\n")

        f.write("## 1. Lessons Learned\n\n")
        if lessons:
            for lesson in lessons:
                bp = "⭐ " if lesson["is_best_practice"] else ""
                f.write(f"### {bp}{lesson['title']}\n\n")
                f.write(f"- **Category:** {lesson['category']}\n")
                f.write(f"- **Description:** {lesson['description']}\n")
                f.write(f"- **Impact:** {lesson['impact']}\n")
                f.write(f"- **Recommendation:** {lesson['recommendation']}\n")
                if lesson.get("tags"):
                    f.write(f"- **Tags:** `{lesson['tags']}`\n")
                f.write("\n---\n\n")
        else:
            f.write("No lessons recorded yet.\n\n")

        f.write("## 2. Best Practices\n\n")
        if best_practices:
            for bp in best_practices:
                f.write(f"### ⭐ {bp['title']}\n\n")
                f.write(f"- **Description:** {bp['description']}\n")
                f.write(f"- **Impact:** {bp['impact']}\n")
                f.write(f"- **Recommendation:** {bp['recommendation']}\n")
                if bp.get("tags"):
                    f.write(f"- **Tags:** `{bp['tags']}`\n")
                f.write("\n---\n\n")
        else:
            f.write("No best practices recorded yet.\n\n")

        f.write("## 3. Reusable Workflows\n\n")
        f.write("The following workflows were validated in this project:\n\n")
        f.write("1. **Project Kickoff Workflow** — Lead creation → planning → resource allocation\n")
        f.write("2. **Progress Tracking Workflow** — Daily tracking → weekly reporting → monthly executive\n")
        f.write("3. **Quality Workflow** — QA checkpoints → testing → readiness verification\n")
        f.write("4. **Delivery Workflow** — Requirements check → QA approval → delivery package\n\n")

        f.write("---\n\n")

        f.write("## 4. Templates Available\n\n")
        f.write("- Project Plan Template (see 01_master_project_plan.md)\n")
        f.write("- Resource Assignment Template (see 02_resource_assignment_report.md)\n")
        f.write("- Task Dashboard Template (see 03_task_dashboard.md)\n")
        f.write("- Risk Register Template (see 06_risk_register.md)\n")
        f.write("- Budget Report Template (see 08_budget_health_report.md)\n")
        f.write("- QA Readiness Template (see 10_qa_readiness_report.md)\n")
        f.write("- Delivery Package Template (see 11_project_delivery_package.md)\n")
