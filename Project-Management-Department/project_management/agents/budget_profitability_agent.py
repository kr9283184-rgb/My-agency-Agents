import os
from datetime import datetime
from typing import Optional
from project_management.agents.base_agent import BaseAgent


class BudgetProfitabilityAgent(BaseAgent):
    HOURLY_RATES = {
        "development": 75,
        "design": 65,
        "project_management": 50,
        "qa": 45,
        "consulting": 100,
    }

    def track_budget(self, project: dict, output_dir: str = "") -> dict:
        project_id = project.get("project_id", "")
        company = project.get("company_name", "")
        deal_amount = project.get("deal_amount", 0)

        existing = self.db.get_budget(project_id)
        if not existing:
            entries = self._create_budget_entries(project)
            for entry in entries:
                self.db.add_budget_entry(entry)
        else:
            entries = existing

        summary = self.db.get_budget_summary(project_id)

        file_path = ""
        if output_dir:
            company_dir = os.path.join(output_dir, company.replace(" ", "_"))
            os.makedirs(company_dir, exist_ok=True)
            file_path = os.path.join(company_dir, "08_budget_health_report.md")
            with open(file_path, "w") as f:
                self._write_report(f, project, summary, entries)

        self.log(f"Budget report generated for {company} — health: {summary['budget_health']}, margin: {summary['profit_margin_pct']:.1f}%")

        return {
            "file_path": file_path,
            "summary": summary,
            "entries": entries,
        }

    def _create_budget_entries(self, project: dict) -> list:
        proposal_type = project.get("proposal_type", "service")
        deal_amount = project.get("deal_amount", 0)

        budget_templates = {
            "website": [
                ("project_management", 40, 2000),
                ("design", 40, 2600),
                ("development", 80, 6000),
            ],
            "automation": [
                ("project_management", 40, 2000),
                ("development", 80, 6000),
                ("consulting", 20, 2000),
            ],
            "seo": [
                ("project_management", 20, 1000),
                ("development", 40, 3000),
                ("consulting", 30, 3000),
            ],
        }

        template = budget_templates.get(proposal_type, budget_templates["website"])
        total_budgeted = sum(h * sum(v for k, v in self.HOURLY_RATES.items() if k == cat) for cat, h, _ in template)
        scale = deal_amount / total_budgeted if total_budgeted > 0 else 1

        entries = []
        for category, hours, base_cost in template:
            rate = self.HOURLY_RATES.get(category, 75)
            adjusted_hours = hours * scale
            adjusted_cost = adjusted_hours * rate
            entries.append({
                "project_id": project["project_id"],
                "category": category,
                "budgeted_hours": round(adjusted_hours, 1),
                "actual_hours": 0,
                "budgeted_cost": round(adjusted_cost, 2),
                "actual_cost": 0,
                "notes": f"Auto-budgeted for {proposal_type} project",
            })
        return entries

    def log_hours(self, project_id: str, category: str, hours: float, cost: float) -> bool:
        entries = self.db.get_budget(project_id)
        for entry in entries:
            if entry["category"] == category:
                new_hours = entry["actual_hours"] + hours
                new_cost = entry["actual_cost"] + cost
                self.db.update_budget_actuals(entry["budget_id"], new_hours, new_cost)
                return True
        return False

    def _write_report(self, f, project: dict, summary: dict, entries: list):
        company = project.get("company_name", "")

        f.write(f"# Budget Health & Profitability Report — {company}\n\n")
        f.write("---\n\n")

        f.write("## 1. Budget Overview\n\n")
        f.write(f"- **Deal Amount:** ${summary['deal_amount']:,.2f}\n")
        f.write(f"- **Total Budgeted Cost:** ${summary['total_budgeted_cost']:,.2f}\n")
        f.write(f"- **Total Actual Cost:** ${summary['total_actual_cost']:,.2f}\n")
        f.write(f"- **Total Budgeted Hours:** {summary['total_budgeted_hours']:.1f}\n")
        f.write(f"- **Total Actual Hours:** {summary['total_actual_hours']:.1f}\n\n")

        health_icon = "✅" if summary["budget_health"] == "healthy" else "⚠️"
        f.write(f"**Budget Health:** {health_icon} {summary['budget_health']}\n\n")

        f.write("---\n\n")

        f.write("## 2. Profitability\n\n")
        f.write(f"- **Revenue:** ${summary['deal_amount']:,.2f}\n")
        f.write(f"- **Total Costs:** ${summary['total_actual_cost']:,.2f}\n")
        f.write(f"- **Profit:** ${summary['profit']:,.2f}\n")
        f.write(f"- **Profit Margin:** {summary['profit_margin_pct']:.1f}%\n\n")

        if summary["profit_margin_pct"] >= 30:
            f.write("**Margin Status:** ✅ Healthy\n\n")
        elif summary["profit_margin_pct"] >= 15:
            f.write("**Margin Status:** ⚠️ Acceptable — Monitor closely\n\n")
        else:
            f.write("**Margin Status:** 🔴 Low — Review costs urgently\n\n")

        f.write("---\n\n")

        f.write("## 3. Category Breakdown\n\n")
        f.write("| Category | Budgeted Hours | Actual Hours | Budgeted Cost | Actual Cost | Variance |\n")
        f.write("|----------|---------------|--------------|---------------|-------------|----------|\n")
        for e in entries:
            variance = e["budgeted_cost"] - e["actual_cost"]
            f.write(f"| {e['category']} | {e['budgeted_hours']:.1f} | {e['actual_hours']:.1f} | ${e['budgeted_cost']:,.2f} | ${e['actual_cost']:,.2f} | ${variance:+,.2f} |\n")
        f.write("\n")

        f.write("---\n\n")

        f.write("## 4. Recommendations\n\n")
        if summary["budget_health"] == "over_budget":
            f.write("- ⚠️ **Over budget!** Review costs and identify savings\n")
            f.write("- Consider change request if additional budget is needed\n")
        else:
            f.write("- ✅ Budget is on track\n")
        if summary["profit_margin_pct"] < 20:
            f.write("- 📋 Look for efficiency improvements to increase margin\n")
        f.write("- 📋 Track hours weekly to maintain budget visibility\n")
        f.write("- 📋 Report any significant variances immediately\n")
