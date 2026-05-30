import os
from datetime import datetime
from typing import Optional
from project_management.agents.base_agent import BaseAgent


class RiskManagementAgent(BaseAgent):
    RISK_CATEGORIES = [
        "delay", "missing_assets", "scope_creep", "resource_shortage",
        "technical_blocker", "client_side_delay", "budget", "quality",
    ]

    def manage_risks(self, project: dict, output_dir: str = "") -> dict:
        project_id = project.get("project_id", "")
        company = project.get("company_name", "")

        existing_risks = self.db.get_risks(project_id)
        identified_risks = self._identify_initial_risks(project)

        for risk in identified_risks:
            risk["project_id"] = project_id
            rid = self.db.add_risk(risk)
            risk["risk_id"] = rid

        all_risks = self.db.get_risks(project_id)

        risk_score = self._calculate_risk_score(all_risks)

        file_path = ""
        if output_dir:
            company_dir = os.path.join(output_dir, company.replace(" ", "_"))
            os.makedirs(company_dir, exist_ok=True)
            file_path = os.path.join(company_dir, "06_risk_register.md")
            with open(file_path, "w") as f:
                self._write_register(f, project, all_risks, risk_score)

        self.log(f"Risk register generated for {company} — {len(all_risks)} risks identified, score: {risk_score}")

        return {
            "file_path": file_path,
            "risks": all_risks,
            "risk_score": risk_score,
            "risk_count": len(all_risks),
        }

    def _identify_initial_risks(self, project: dict) -> list:
        risks = []
        proposal_type = project.get("proposal_type", "service")
        deal_amount = project.get("deal_amount", 0)

        common_risks = [
            {
                "title": "Client asset delivery delay",
                "description": "Client may delay providing brand assets, content, or approvals",
                "category": "missing_assets",
                "risk_score": 6,
                "impact_level": "medium",
                "probability": "medium",
                "mitigation_plan": "Set clear deadlines for asset delivery; send reminders 1 week before due date",
                "escalation_plan": "Escalate to Account Manager if assets not received within 1 week of deadline",
            },
            {
                "title": "Scope creep during development",
                "description": "Client may request additional features beyond original scope",
                "category": "scope_creep",
                "risk_score": 7,
                "impact_level": "high",
                "probability": "medium",
                "mitigation_plan": "Document scope clearly in SOW; require change request for any additions",
                "escalation_plan": "Submit change request with cost/timeline impact for client approval",
            },
            {
                "title": "Technical integration issues",
                "description": "Integration with client systems may encounter technical challenges",
                "category": "technical_blocker",
                "risk_score": 5,
                "impact_level": "medium",
                "probability": "medium",
                "mitigation_plan": "Conduct technical feasibility assessment early; identify integration points",
                "escalation_plan": "Engage senior engineering team if issue cannot be resolved within 3 days",
            },
        ]

        if proposal_type == "automation":
            common_risks.append({
                "title": "Process complexity underestimated",
                "description": "Business processes may be more complex than initially assessed",
                "category": "technical_blocker",
                "risk_score": 8,
                "impact_level": "high",
                "probability": "medium",
                "mitigation_plan": "Conduct thorough process discovery; include buffer in timeline",
                "escalation_plan": "Re-scope project with updated timeline and cost if complexity exceeds estimates",
            })

        if deal_amount < 3000:
            common_risks.append({
                "title": "Budget constraint limiting quality",
                "description": "Small budget may limit development hours and quality",
                "category": "budget",
                "risk_score": 6,
                "impact_level": "medium",
                "probability": "high",
                "mitigation_plan": "Prioritize core features; use efficient workflows and templates",
                "escalation_plan": "Discuss phased approach with client if additional budget needed",
            })

        risks.extend(common_risks)
        return risks

    def _calculate_risk_score(self, risks: list) -> int:
        if not risks:
            return 0
        open_risks = [r for r in risks if r["status"] == "open"]
        if not open_risks:
            return 0
        return sum(r["risk_score"] for r in open_risks)

    def _write_register(self, f, project: dict, risks: list, risk_score: int):
        company = project.get("company_name", "")
        open_risks = [r for r in risks if r["status"] == "open"]
        closed_risks = [r for r in risks if r["status"] != "open"]

        f.write(f"# Risk Register — {company}\n\n")
        f.write("---\n\n")

        f.write("## 1. Risk Summary\n\n")
        f.write(f"- **Total Risks:** {len(risks)}\n")
        f.write(f"- **Open Risks:** {len(open_risks)}\n")
        f.write(f"- **Closed/Mitigated:** {len(closed_risks)}\n")
        f.write(f"- **Overall Risk Score:** {risk_score}\n\n")

        risk_level = "LOW" if risk_score < 10 else "MEDIUM" if risk_score < 20 else "HIGH"
        f.write(f"**Risk Level:** {risk_level}\n\n")

        f.write("---\n\n")

        f.write("## 2. Active Risks\n\n")
        if open_risks:
            for r in open_risks:
                icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(r["impact_level"], "⚪")
                f.write(f"### {icon} {r['title']}\n\n")
                f.write(f"- **Category:** {r['category']}\n")
                f.write(f"- **Risk Score:** {r['risk_score']}/10\n")
                f.write(f"- **Impact Level:** {r['impact_level']}\n")
                f.write(f"- **Probability:** {r['probability']}\n")
                f.write(f"- **Description:** {r['description']}\n\n")
                f.write("**Mitigation Plan:**\n")
                f.write(f"{r['mitigation_plan']}\n\n")
                f.write("**Escalation Plan:**\n")
                f.write(f"{r['escalation_plan']}\n\n")
                f.write("---\n\n")
        else:
            f.write("No active risks. ✅\n\n")

        if closed_risks:
            f.write("## 3. Closed/Mitigated Risks\n\n")
            for r in closed_risks:
                f.write(f"- ✅ **{r['title']}** — {r.get('status', 'mitigated')}\n")
            f.write("\n")
