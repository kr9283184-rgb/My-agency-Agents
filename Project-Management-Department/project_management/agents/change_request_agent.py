import os
from datetime import datetime
from typing import Optional
from project_management.agents.base_agent import BaseAgent


class ChangeRequestAgent(BaseAgent):
    def process_change_request(self, project: dict, cr_data: dict, output_dir: str = "") -> dict:
        project_id = project.get("project_id", "")
        company = project.get("company_name", "")

        impact = self._analyze_impact(project, cr_data)
        cr_entry = {
            "project_id": project_id,
            "title": cr_data.get("title", "Change Request"),
            "description": cr_data.get("description", ""),
            "requested_by": cr_data.get("requested_by", "Client"),
            "impact_analysis": impact["analysis"],
            "estimated_effort_hours": impact["effort_hours"],
            "timeline_impact_days": impact["timeline_days"],
            "cost_impact": impact["cost"],
            "status": "pending",
        }
        cr_id = self.db.add_change_request(cr_entry)
        cr_entry["cr_id"] = cr_id

        file_path = ""
        if output_dir:
            company_dir = os.path.join(output_dir, company.replace(" ", "_"))
            os.makedirs(company_dir, exist_ok=True)
            file_path = os.path.join(company_dir, "07_change_request_report.md")
            with open(file_path, "w") as f:
                self._write_report(f, project, cr_entry, impact)

        self.log(f"Change request processed for {company} — {cr_entry['title']} ({impact['effort_hours']}h impact)")

        return {
            "file_path": file_path,
            "change_request": cr_entry,
            "impact": impact,
            "status": "pending_approval",
        }

    def _analyze_impact(self, project: dict, cr_data: dict) -> dict:
        effort_hours = cr_data.get("estimated_hours", 0)
        complexity = cr_data.get("complexity", "medium")

        complexity_multiplier = {"low": 0.5, "medium": 1.0, "high": 2.0}
        multiplier = complexity_multiplier.get(complexity, 1.0)
        adjusted_hours = effort_hours * multiplier

        deal_amount = project.get("deal_amount", 0)
        hourly_rate = deal_amount / 80 if deal_amount > 0 else 75
        timeline_days = max(1, int(adjusted_hours / 4))
        cost = adjusted_hours * hourly_rate

        analysis = (
            f"Change request analysis:\n"
            f"- Estimated effort: {adjusted_hours:.0f} hours\n"
            f"- Complexity: {complexity}\n"
            f"- Timeline impact: {timeline_days} days\n"
            f"- Cost impact: ${cost:,.2f}\n"
            f"- Hourly rate used: ${hourly_rate:.2f}/h\n\n"
            f"Recommendation: {'Proceed with approval' if cost < deal_amount * 0.2 else 'Review budget implications before approval'}"
        )

        return {
            "effort_hours": round(adjusted_hours, 1),
            "timeline_days": timeline_days,
            "cost": round(cost, 2),
            "hourly_rate": round(hourly_rate, 2),
            "analysis": analysis,
        }

    def approve_request(self, cr_id: int, approved_by: str, approved: bool, reason: str = "") -> dict:
        self.db.approve_change_request(cr_id, approved_by, approved, reason)
        cr = None
        with self.db._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM change_requests WHERE cr_id = ?", (cr_id,)
            ).fetchone()
            cr = dict(row) if row else {}
        status = "approved" if approved else "rejected"
        self.log(f"Change request {cr_id} {status} by {approved_by}")
        return {"cr_id": cr_id, "status": status, "change_request": cr}

    def _write_report(self, f, project: dict, cr_entry: dict, impact: dict):
        company = project.get("company_name", "")
        deal_amount = project.get("deal_amount", 0)

        f.write(f"# Change Request Report — {company}\n\n")
        f.write("---\n\n")

        f.write("## 1. Change Request Details\n\n")
        f.write(f"- **Title:** {cr_entry['title']}\n")
        f.write(f"- **Requested By:** {cr_entry['requested_by']}\n")
        f.write(f"- **Description:** {cr_entry['description']}\n")
        f.write(f"- **Status:** {cr_entry['status']}\n\n")

        f.write("---\n\n")

        f.write("## 2. Impact Analysis\n\n")
        f.write(f"- **Estimated Effort:** {impact['effort_hours']} hours\n")
        f.write(f"- **Timeline Impact:** {impact['timeline_days']} days\n")
        f.write(f"- **Cost Impact:** ${impact['cost']:,.2f}\n")
        f.write(f"- **Hourly Rate:** ${impact['hourly_rate']:.2f}\n\n")

        f.write("### Analysis\n\n")
        f.write(f"{impact['analysis']}\n\n")

        f.write("---\n\n")

        f.write("## 3. Financial Impact\n\n")
        f.write(f"- **Current Deal Value:** ${float(deal_amount):,.2f}\n")
        f.write(f"- **Change Cost:** ${impact['cost']:,.2f}\n")
        if deal_amount > 0:
            pct = (impact["cost"] / deal_amount) * 100
            f.write(f"- **Percentage of Deal:** {pct:.1f}%\n")
            f.write(f"- **Revised Deal Value:** ${deal_amount + impact['cost']:,.2f}\n\n")

        f.write("---\n\n")

        f.write("## 4. Approval\n\n")
        f.write("- [ ] **Pending Approval** — Awaiting client decision\n")
        f.write("- [ ] **Approved** — Update project plan and proceed\n")
        f.write("- [ ] **Rejected** — No changes to scope\n\n")

        f.write("---\n\n")

        f.write("## 5. Next Steps\n\n")
        f.write("1. Submit change request to client for review\n")
        f.write("2. If approved: Update project plan, timeline, and budget\n")
        f.write("3. If rejected: Document decision and continue as planned\n")
        f.write("4. Communicate decision to all stakeholders\n")
