import os
from datetime import datetime
from typing import Optional
from project_management.agents.base_agent import BaseAgent


class TeamCoordinationAgent(BaseAgent):
    def coordinate_teams(self, project: dict, output_dir: str = "") -> dict:
        project_id = project.get("project_id", "")
        company = project.get("company_name", "")

        resource_summary = self.db.get_resource_summary(project_id)
        tasks = self.db.get_tasks(project_id)
        milestones = self.db.get_milestones(project_id)

        dept_tasks = self._organize_by_department(resource_summary, tasks)
        handoff_points = self._identify_handoffs(milestones)
        conflicts = self._detect_conflicts(resource_summary, tasks)

        file_path = ""
        if output_dir:
            company_dir = os.path.join(output_dir, company.replace(" ", "_"))
            os.makedirs(company_dir, exist_ok=True)
            file_path = os.path.join(company_dir, "04_coordination_report.md")
            with open(file_path, "w") as f:
                self._write_report(f, project, resource_summary, dept_tasks, handoff_points, conflicts)

        self.log(f"Coordination report generated for {company} — {len(dept_tasks)} departments coordinated")

        return {
            "file_path": file_path,
            "departments": list(dept_tasks.keys()),
            "handoff_points": handoff_points,
            "conflicts": conflicts,
        }

    def _organize_by_department(self, resource_summary: dict, tasks: list) -> dict:
        dept_map = {}
        for dept, info in resource_summary.get("by_department", {}).items():
            dept_map[dept] = {
                "members": info["members"],
                "tasks": [],
                "total_hours": 0,
            }
        for task in tasks:
            owner = task.get("owner", "unassigned")
            assigned = False
            for dept, info in dept_map.items():
                if owner in info["members"] or any(owner.startswith(m.split()[0].lower()) for m in info["members"] if m):
                    info["tasks"].append(task)
                    info["total_hours"] += task.get("estimated_hours", 0)
                    assigned = True
                    break
            if not assigned:
                if "Unassigned" not in dept_map:
                    dept_map["Unassigned"] = {"members": [], "tasks": [], "total_hours": 0}
                dept_map["Unassigned"]["tasks"].append(task)
                dept_map["Unassigned"]["total_hours"] += task.get("estimated_hours", 0)
        return dept_map

    def _identify_handoffs(self, milestones: list) -> list:
        handoffs = []
        for i, m in enumerate(milestones):
            if i < len(milestones) - 1:
                handoffs.append({
                    "from_phase": m["title"],
                    "to_phase": milestones[i + 1]["title"],
                    "milestone_id": m.get("milestone_id", 0),
                    "status": m["status"],
                })
        return handoffs

    def _detect_conflicts(self, resource_summary: dict, tasks: list) -> list:
        conflicts = []
        for dept, info in resource_summary.get("by_department", {}).items():
            if info["total_allocation"] > 200:
                conflicts.append({
                    "department": dept,
                    "type": "over_allocation",
                    "description": f"Department {dept} has {info['total_allocation']}% total allocation — may exceed capacity",
                    "severity": "medium",
                })
        high_priority_unassigned = [t for t in tasks if t["priority"] == "high" and not t["owner"]]
        if high_priority_unassigned:
            conflicts.append({
                "department": "all",
                "type": "unassigned_high_priority",
                "description": f"{len(high_priority_unassigned)} high-priority tasks unassigned",
                "severity": "high",
            })
        return conflicts

    def _write_report(self, f, project: dict, resource_summary: dict, dept_tasks: dict, handoffs: list, conflicts: list):
        company = project.get("company_name", "")

        f.write(f"# Team Coordination Report — {company}\n\n")
        f.write("---\n\n")

        f.write("## 1. Department Overview\n\n")
        f.write("| Department | Members | Total Tasks | Total Hours |\n")
        f.write("|------------|---------|-------------|-------------|\n")
        for dept, info in sorted(dept_tasks.items()):
            f.write(f"| {dept} | {', '.join(info['members']) if info['members'] else '-'} | {len(info['tasks'])} | {info['total_hours']}h |\n")
        f.write("\n")

        f.write("---\n\n")

        f.write("## 2. Handoff Points\n\n")
        f.write("| From | To | Status |\n")
        f.write("|------|-----|--------|\n")
        for h in handoffs:
            f.write(f"| {h['from_phase']} | {h['to_phase']} | {h['status']} |\n")
        f.write("\n")

        f.write("---\n\n")

        f.write("## 3. Detected Conflicts\n\n")
        if conflicts:
            f.write("| Department | Type | Description | Severity |\n")
            f.write("|------------|------|-------------|----------|\n")
            for c in conflicts:
                f.write(f"| {c['department']} | {c['type']} | {c['description']} | {c['severity']} |\n")
        else:
            f.write("No conflicts detected.\n")
        f.write("\n")

        f.write("---\n\n")

        f.write("## 4. Recommendations\n\n")
        if conflicts:
            f.write("### Action Required\n\n")
            for c in conflicts:
                if c["severity"] == "high":
                    f.write(f"- ⚠️ {c['description']} — Assign owners and resolve immediately\n")
                else:
                    f.write(f"- 📋 {c['description']} — Review and address\n")
        else:
            f.write("- All departments are well-coordinated.\n")
        f.write("- Schedule weekly cross-team sync meetings.\n")
        f.write("- Ensure handoff documentation is prepared before phase transitions.\n")
