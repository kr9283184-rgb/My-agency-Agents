import os
from typing import Optional
from project_management.agents.base_agent import BaseAgent


TASK_STATES = ["pending", "assigned", "in_progress", "review", "testing", "completed"]


class TaskManagementAgent(BaseAgent):
    def manage_tasks(self, project: dict, output_dir: str = "") -> dict:
        project_id = project.get("project_id", "")
        company = project.get("company_name", "")

        dashboard = self.db.get_task_dashboard(project_id)
        tasks = dashboard["tasks"]

        file_path = ""
        if output_dir:
            company_dir = os.path.join(output_dir, company.replace(" ", "_"))
            os.makedirs(company_dir, exist_ok=True)
            file_path = os.path.join(company_dir, "03_task_dashboard.md")
            with open(file_path, "w") as f:
                self._write_dashboard(f, project, dashboard)

        self.log(f"Task dashboard generated for {company} — {dashboard['total']} tasks tracked")

        return {
            "file_path": file_path,
            "dashboard": dashboard,
        }

    def assign_task(self, task_id: int, owner: str) -> bool:
        self.db.update_task(task_id, {"owner": owner, "state": "assigned"})
        self.log(f"Task {task_id} assigned to {owner}")
        return True

    def start_task(self, task_id: int) -> bool:
        self.db.update_task_state(task_id, "in_progress", 0.0)
        return True

    def complete_task(self, task_id: int) -> bool:
        self.db.update_task_state(task_id, "completed", 100.0)
        return True

    def update_task_progress(self, task_id: int, progress_pct: float) -> bool:
        state = "in_progress"
        if progress_pct >= 100:
            state = "completed"
        elif progress_pct > 0:
            state = "in_progress"
        self.db.update_task_state(task_id, state, progress_pct)
        return True

    def _write_dashboard(self, f, project: dict, dashboard: dict):
        company = project.get("company_name", "")
        by_state = dashboard["by_state"]
        by_owner = dashboard["by_owner"]

        f.write(f"# Task Dashboard — {company}\n\n")
        f.write("---\n\n")

        f.write("## 1. Summary\n\n")
        f.write(f"- **Total Tasks:** {dashboard['total']}\n")
        f.write(f"- **By State:**\n")
        for state in TASK_STATES:
            count = by_state.get(state, 0)
            icon = {"pending": "⬜", "assigned": "🟦", "in_progress": "🟨",
                    "review": "🟪", "testing": "🟧", "completed": "✅"}.get(state, "⬜")
            f.write(f"  - {icon} {state.title()}: {count}\n")
        f.write("\n")

        completed = by_state.get("completed", 0)
        total = dashboard["total"]
        completion = (completed / total * 100) if total > 0 else 0
        f.write(f"**Overall Completion:** {completion:.1f}%\n\n")

        f.write("---\n\n")

        f.write("## 2. Tasks by Owner\n\n")
        f.write("| Owner | Count |\n")
        f.write("|-------|-------|\n")
        for owner, count in sorted(by_owner.items()):
            f.write(f"| {owner} | {count} |\n")
        f.write("\n")

        f.write("---\n\n")

        f.write("## 3. All Tasks\n\n")
        f.write("| ID | Title | Owner | Priority | State | Progress | Deadline |\n")
        f.write("|----|-------|-------|----------|-------|----------|----------|\n")
        for task in dashboard["tasks"]:
            f.write(f"| {task['task_id']} | {task['title']} | {task['owner'] or '-'} | {task['priority']} | {task['state']} | {task['progress_pct']}% | {task.get('deadline', '-')} |\n")
        f.write("\n")

        f.write("---\n\n")

        f.write("## 4. Next Actions\n\n")
        pending_tasks = [t for t in dashboard["tasks"] if t["state"] == "pending"]
        if pending_tasks:
            f.write("### Pending (need assignment)\n\n")
            for t in pending_tasks[:5]:
                f.write(f"- **{t['title']}** ({t['priority']}) — {t['estimated_hours']}h estimated\n")
        in_progress_tasks = [t for t in dashboard["tasks"] if t["state"] == "in_progress"]
        if in_progress_tasks:
            f.write("\n### In Progress\n\n")
            for t in in_progress_tasks:
                f.write(f"- **{t['title']}** — {t['progress_pct']}% complete ({t['owner']})\n")
