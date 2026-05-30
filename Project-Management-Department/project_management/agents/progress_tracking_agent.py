import os
from datetime import datetime
from typing import Optional
from project_management.agents.base_agent import BaseAgent


class ProgressTrackingAgent(BaseAgent):
    def track_progress(self, project: dict, output_dir: str = "", report_type: str = "daily") -> dict:
        project_id = project.get("project_id", "")
        company = project.get("company_name", "")

        project_data = self.db.get_project(project_id) or project
        milestones = self.db.get_milestones(project_id)
        tasks = self.db.get_tasks(project_id)
        risks = self.db.get_risks(project_id, "open")

        completion_pct = self._calculate_completion(tasks, project_data)
        milestone_status = self._get_milestone_status(milestones)
        productivity = self._calculate_productivity(tasks)
        delay_indicators = self._detect_delays(milestones, tasks)

        if project_data:
            self.db.update_project_status(project_id, project_data.get("status", "in_progress"), completion_pct)

        file_path = ""
        if output_dir:
            company_dir = os.path.join(output_dir, company.replace(" ", "_"))
            os.makedirs(company_dir, exist_ok=True)
            report_name = {"daily": "05_daily_progress", "weekly": "05_weekly_progress", "monthly": "05_monthly_executive"}.get(report_type, "05_daily_progress")
            file_path = os.path.join(company_dir, f"{report_name}_report.md")
            with open(file_path, "w") as f:
                self._write_report(f, project, report_type, completion_pct, milestone_status, productivity, delay_indicators, tasks, risks)

        self.log(f"{report_type.title()} progress report generated for {company} — {completion_pct:.1f}% complete")

        return {
            "file_path": file_path,
            "report_type": report_type,
            "completion_pct": completion_pct,
            "milestone_status": milestone_status,
            "productivity": productivity,
            "delay_indicators": delay_indicators,
        }

    def _calculate_completion(self, tasks: list, project: dict) -> float:
        if not tasks:
            return project.get("completion_pct", 0.0)
        total_estimated = sum(t.get("estimated_hours", 0) for t in tasks)
        if total_estimated == 0:
            return 0.0
        total_actual = sum(t.get("actual_hours", 0) for t in tasks)
        completed = sum(1 for t in tasks if t["state"] == "completed")
        return min((completed / len(tasks)) * 100, 100)

    def _get_milestone_status(self, milestones: list) -> list:
        return [
            {
                "title": m["title"],
                "phase": m["phase"],
                "status": m["status"],
                "completion_pct": m["completion_pct"],
                "due_date": m.get("due_date", ""),
            }
            for m in milestones
        ]

    def _calculate_productivity(self, tasks: list) -> dict:
        total_estimated = sum(t.get("estimated_hours", 0) for t in tasks)
        total_actual = sum(t.get("actual_hours", 0) for t in tasks)
        completed = [t for t in tasks if t["state"] == "completed"]
        completed_estimated = sum(t.get("estimated_hours", 0) for t in completed)
        completed_actual = sum(t.get("actual_hours", 0) for t in completed)
        productivity_ratio = completed_estimated / completed_actual if completed_actual > 0 else 1.0
        return {
            "total_estimated_hours": total_estimated,
            "total_actual_hours": total_actual,
            "completed_estimated": completed_estimated,
            "completed_actual": completed_actual,
            "productivity_ratio": productivity_ratio,
            "efficiency_pct": min(productivity_ratio * 100, 200),
        }

    def _detect_delays(self, milestones: list, tasks: list) -> list:
        indicators = []
        today = datetime.now().date()

        for m in milestones:
            if m.get("due_date") and m["status"] != "completed":
                try:
                    due = datetime.strptime(m["due_date"], "%Y-%m-%d").date()
                    if due < today:
                        days_late = (today - due).days
                        indicators.append({
                            "type": "milestone_overdue",
                            "item": m["title"],
                            "days_late": days_late,
                            "severity": "high" if days_late > 7 else "medium",
                        })
                except ValueError:
                    pass

        for t in tasks:
            if t.get("deadline") and t["state"] not in ("completed", "testing"):
                try:
                    due = datetime.strptime(t["deadline"], "%Y-%m-%d").date()
                    if due < today and due > datetime(2020, 1, 1).date():
                        days_late = (today - due).days
                        indicators.append({
                            "type": "task_overdue",
                            "item": t["title"],
                            "days_late": days_late,
                            "severity": "medium" if days_late > 3 else "low",
                        })
                except ValueError:
                    pass

        pending_count = sum(1 for t in tasks if t["state"] == "pending")
        total = len(tasks)
        if total > 0 and pending_count / total > 0.5:
            indicators.append({
                "type": "high_pending_ratio",
                "item": f"{pending_count}/{total} tasks pending",
                "days_late": 0,
                "severity": "medium",
            })

        return indicators

    def _write_report(self, f, project: dict, report_type: str, completion_pct: float,
                      milestone_status: list, productivity: dict, delay_indicators: list,
                      tasks: list, risks: list):
        company = project.get("company_name", "")
        status = project.get("status", "in_progress")

        report_title = {
            "daily": "Daily Progress Report",
            "weekly": "Weekly Progress Report",
            "monthly": "Monthly Executive Report",
        }.get(report_type, "Progress Report")

        f.write(f"# {report_title} — {company}\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**Status:** {status}\n\n")
        f.write("---\n\n")

        bar_len = 30
        filled = int((completion_pct / 100) * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)

        f.write("## 1. Overall Progress\n\n")
        f.write(f"**Completion:** {completion_pct:.1f}%\n")
        f.write(f"**Progress Bar:** {bar}\n\n")

        f.write("---\n\n")

        f.write("## 2. Milestone Status\n\n")
        f.write("| Milestone | Phase | Status | Progress | Due Date |\n")
        f.write("|-----------|-------|--------|----------|----------|\n")
        for ms in milestone_status:
            icon = {"completed": "✅", "in_progress": "🔄", "pending": "⬜", "delayed": "⚠️"}.get(ms["status"], "⬜")
            f.write(f"| {icon} {ms['title']} | {ms['phase']} | {ms['status']} | {ms['completion_pct']}% | {ms.get('due_date', '-')} |\n")
        f.write("\n")

        f.write("---\n\n")

        f.write("## 3. Productivity Metrics\n\n")
        f.write(f"- **Total Estimated Hours:** {productivity['total_estimated_hours']:.1f}\n")
        f.write(f"- **Total Actual Hours:** {productivity['total_actual_hours']:.1f}\n")
        f.write(f"- **Completed Estimated Hours:** {productivity['completed_estimated']:.1f}\n")
        f.write(f"- **Completed Actual Hours:** {productivity['completed_actual']:.1f}\n")
        f.write(f"- **Productivity Ratio:** {productivity['productivity_ratio']:.2f}x\n")
        f.write(f"- **Efficiency:** {productivity['efficiency_pct']:.1f}%\n\n")

        f.write("---\n\n")

        f.write("## 4. Delay Indicators\n\n")
        if delay_indicators:
            f.write("| Type | Item | Days Late | Severity |\n")
            f.write("|------|------|-----------|----------|\n")
            for d in delay_indicators:
                icon = "🔴" if d["severity"] == "high" else "🟡" if d["severity"] == "medium" else "🟢"
                f.write(f"| {icon} {d['type']} | {d['item']} | {d['days_late']}d | {d['severity']} |\n")
        else:
            f.write("No delays detected.\n")
        f.write("\n")

        if report_type in ("weekly", "monthly"):
            f.write("---\n\n")
            f.write("## 5. Task Distribution\n\n")
            by_state = {}
            for t in tasks:
                by_state[t["state"]] = by_state.get(t["state"], 0) + 1
            f.write("| State | Count |\n")
            f.write("|-------|-------|\n")
            for state in ["pending", "assigned", "in_progress", "review", "testing", "completed"]:
                if state in by_state:
                    f.write(f"| {state} | {by_state[state]} |\n")
            f.write("\n")

        if report_type == "monthly":
            f.write("---\n\n")
            f.write("## 6. Active Risks\n\n")
            if risks:
                f.write("| Risk | Score | Impact | Status |\n")
                f.write("|------|-------|--------|--------|\n")
                for r in risks:
                    f.write(f"| {r['title']} | {r['risk_score']} | {r['impact_level']} | {r['status']} |\n")
            else:
                f.write("No active risks.\n")
            f.write("\n")

            f.write("---\n\n")
            f.write("## 7. Recommendations\n\n")
            if delay_indicators:
                f.write("### ⚠️ Delays Need Attention\n\n")
                for d in delay_indicators:
                    if d["severity"] == "high":
                        f.write(f"- Escalate: {d['item']} is {d['days_late']} days overdue\n")
                f.write("\n")
            f.write("### Next Steps\n\n")
            f.write("- Continue monitoring milestone progress\n")
            f.write("- Address any blocked tasks\n")
            f.write("- Prepare for upcoming phase handoffs\n")
            f.write("- Update risk mitigation plans\n")
