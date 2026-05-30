import os
from datetime import datetime
from typing import Optional
from project_management.agents.base_agent import BaseAgent


class QualityCoordinationAgent(BaseAgent):
    ACCEPTANCE_CRITERIA_TEMPLATES = {
        "website": [
            ("Responsive Design", "All pages render correctly on desktop, tablet, and mobile devices"),
            ("Cross-Browser Compatibility", "Works on Chrome, Firefox, Safari, and Edge"),
            ("Page Speed", "Load time under 3 seconds on standard connection"),
            ("SEO Basics", "Meta tags, headings, alt text, and sitemap in place"),
            ("Contact Forms", "All forms submit correctly and send notifications"),
            ("Navigation", "All links work correctly, no broken links"),
            ("Content Accuracy", "All content matches approved copy"),
        ],
        "automation": [
            ("Workflow Execution", "Automated workflows run without errors"),
            ("Data Accuracy", "Processed data matches expected output"),
            ("Error Handling", "Errors are caught and logged appropriately"),
            ("Integration Tests", "All integrations return expected results"),
            ("Performance", "Automation completes within acceptable time"),
            ("Security", "Authentication and authorization are verified"),
            ("Documentation", "Runbook and user guide are complete"),
        ],
        "seo": [
            ("Keyword Rankings", "Target keywords show improvement"),
            ("Technical SEO", "Crawl errors fixed, sitemap submitted"),
            ("Content Quality", "All content meets editorial standards"),
            ("Meta Optimization", "Title tags and meta descriptions optimized"),
            ("Backlinks", "Quality backlinks acquired as planned"),
            ("Analytics", "Tracking and reporting configured correctly"),
        ],
    }

    def verify_quality(self, project: dict, output_dir: str = "") -> dict:
        project_id = project.get("project_id", "")
        company = project.get("company_name", "")
        proposal_type = project.get("proposal_type", "website")

        existing = self.db.get_quality_checkpoints(project_id)
        if not existing:
            criteria = self.ACCEPTANCE_CRITERIA_TEMPLATES.get(
                proposal_type, self.ACCEPTANCE_CRITERIA_TEMPLATES["website"]
            )
            for checkpoint_name, desc in criteria:
                self.db.add_quality_checkpoint({
                    "project_id": project_id,
                    "checkpoint_name": checkpoint_name,
                    "description": desc,
                    "acceptance_criteria": desc,
                    "status": "pending",
                })

        readiness = self.db.get_qa_readiness(project_id)

        file_path = ""
        if output_dir:
            company_dir = os.path.join(output_dir, company.replace(" ", "_"))
            os.makedirs(company_dir, exist_ok=True)
            file_path = os.path.join(company_dir, "10_qa_readiness_report.md")
            with open(file_path, "w") as f:
                self._write_report(f, project, readiness)

        self.log(f"QA readiness report generated for {company} — readiness: {readiness['readiness_pct']:.0f}%")

        return {
            "file_path": file_path,
            "readiness": readiness,
        }

    def pass_checkpoint(self, qc_id: int, tested_by: str, notes: str = ""):
        self.db.update_quality_checkpoint(qc_id, True, tested_by, notes)
        self.log(f"Quality checkpoint {qc_id} passed by {tested_by}")

    def fail_checkpoint(self, qc_id: int, tested_by: str, notes: str = ""):
        self.db.update_quality_checkpoint(qc_id, False, tested_by, notes)
        self.log(f"Quality checkpoint {qc_id} failed by {tested_by}")

    def _write_report(self, f, project: dict, readiness: dict):
        company = project.get("company_name", "")

        f.write(f"# QA Readiness Report — {company}\n\n")
        f.write("---\n\n")

        f.write("## 1. Summary\n\n")
        f.write(f"- **Total Checkpoints:** {readiness['total']}\n")
        f.write(f"- **Passed:** {readiness['passed']}\n")
        f.write(f"- **Failed:** {readiness['failed']}\n")
        f.write(f"- **Pending:** {readiness['pending']}\n")
        f.write(f"- **Readiness:** {readiness['readiness_pct']:.0f}%\n\n")

        if readiness["ready"]:
            f.write("**Status:** ✅ READY FOR DELIVERY\n\n")
        elif readiness["readiness_pct"] > 50:
            f.write("**Status:** 🟡 IN PROGRESS — Continue testing\n\n")
        else:
            f.write("**Status:** 🔴 NOT READY — Testing required\n\n")

        f.write("---\n\n")

        f.write("## 2. Checkpoint Details\n\n")
        f.write("| Checkpoint | Status | Passed | Tested By | Notes |\n")
        f.write("|------------|--------|--------|-----------|-------|\n")
        for c in readiness["checkpoints"]:
            icon = "✅" if c["passed"] else "❌" if c["status"] == "completed" else "⬜"
            tested = c.get("tested_by", "-")
            notes = c.get("notes", "-")
            f.write(f"| {icon} {c['checkpoint_name']} | {c['status']} | {'Yes' if c['passed'] else 'No'} | {tested} | {notes} |\n")
        f.write("\n")

        f.write("---\n\n")

        f.write("## 3. Failed Items\n\n")
        failed = [c for c in readiness["checkpoints"] if not c["passed"] and c["status"] == "completed"]
        if failed:
            for c in failed:
                f.write(f"### ❌ {c['checkpoint_name']}\n")
                f.write(f"- **Description:** {c.get('description', '')}\n")
                f.write(f"- **Tested By:** {c.get('tested_by', '-')}\n")
                f.write(f"- **Notes:** {c.get('notes', 'No details')}\n\n")
        else:
            f.write("No failed checkpoints.\n\n")

        f.write("## 4. Recommendations\n\n")
        if readiness["ready"]:
            f.write("- ✅ Proceed with delivery\n")
            f.write("- 📋 Prepare delivery documentation\n")
            f.write("- 📋 Schedule client handover\n")
        else:
            remaining = readiness["total"] - readiness["passed"]
            f.write(f"- ⚠️ {remaining} checkpoints remaining\n")
            f.write("- 📋 Prioritize failed items for re-testing\n")
            f.write("- 📋 Assign QA resources to pending items\n")
            f.write("- 📋 Schedule re-review once all items pass\n")
