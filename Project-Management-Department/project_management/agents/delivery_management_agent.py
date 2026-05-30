import os
from datetime import datetime
from typing import Optional
from project_management.agents.base_agent import BaseAgent


class DeliveryManagementAgent(BaseAgent):
    def prepare_delivery(self, project: dict, output_dir: str = "") -> dict:
        project_id = project.get("project_id", "")
        company = project.get("company_name", "")

        project_data = self.db.get_project(project_id) or project
        milestones = self.db.get_milestones(project_id)
        deliverables = self.db.get_deliverables(project_id)
        quality = self.db.get_qa_readiness(project_id)
        tasks = self.db.get_tasks(project_id)

        requirements_met = self._check_requirements(tasks, milestones)
        qa_approved = quality["ready"]
        docs_prepared = len(deliverables) > 0 or len(milestones) > 0

        if requirements_met and qa_approved:
            self.db.update_project_status(project_id, "delivery_ready", 100.0)

        completion_pct = sum(1 for t in tasks if t["state"] == "completed")
        total = len(tasks)

        file_path = ""
        if output_dir:
            company_dir = os.path.join(output_dir, company.replace(" ", "_"))
            os.makedirs(company_dir, exist_ok=True)
            file_path = os.path.join(company_dir, "11_project_delivery_package.md")
            with open(file_path, "w") as f:
                self._write_package(f, project_data, milestones, deliverables, quality,
                                    completion_pct, total, requirements_met, qa_approved)

        self.log(f"Delivery package prepared for {company} — ready for delivery: {requirements_met and qa_approved}")

        return {
            "file_path": file_path,
            "requirements_met": requirements_met,
            "qa_approved": qa_approved,
            "documentation_prepared": docs_prepared,
            "delivery_ready": requirements_met and qa_approved,
        }

    def _check_requirements(self, tasks: list, milestones: list) -> bool:
        if not tasks and not milestones:
            return False
        completed_tasks = sum(1 for t in tasks if t["state"] == "completed")
        all_milestones_done = all(m["status"] == "completed" for m in milestones) if milestones else True
        return completed_tasks == len(tasks) and all_milestones_done

    def _write_package(self, f, project: dict, milestones: list, deliverables: list,
                       quality: dict, completed: int, total: int,
                       requirements_met: bool, qa_approved: bool):
        company = project.get("company_name", "")
        contact = project.get("contact_name", "")
        email = project.get("email", "")
        proposal_type = project.get("proposal_type", "")
        deal_amount = project.get("deal_amount", 0)
        project_id = project.get("project_id", "")

        delivery_ready = requirements_met and qa_approved

        f.write(f"# Project Delivery Package — {company}\n\n")
        f.write("---\n\n")

        f.write("## 1. Delivery Summary\n\n")
        f.write(f"- **Project:** {company}\n")
        f.write(f"- **Project ID:** {project_id}\n")
        f.write(f"- **Client Contact:** {contact} ({email})\n")
        f.write(f"- **Project Type:** {proposal_type}\n")
        f.write(f"- **Deal Value:** ${float(deal_amount):,.2f}\n")
        f.write(f"- **Tasks Completed:** {completed}/{total}\n")
        f.write(f"- **QA Readiness:** {quality['readiness_pct']:.0f}%\n\n")

        if delivery_ready:
            f.write("**Status:** ✅ READY FOR DELIVERY\n\n")
        else:
            f.write("**Status:** ⚠️ PENDING — See checklist below\n\n")

        f.write("---\n\n")

        f.write("## 2. Delivery Checklist\n\n")
        f.write("| Requirement | Status |\n")
        f.write("|-------------|--------|\n")
        f.write(f"| Requirements Complete | {'✅' if requirements_met else '❌'} |\n")
        f.write(f"| QA Approved | {'✅' if qa_approved else '❌'} |\n")
        f.write(f"| Documentation Prepared | {'✅' if len(deliverables) > 0 else '✅' if len(milestones) > 0 else '❌'} |\n")
        f.write(f"| Client Package Ready | {'✅' if delivery_ready else '❌'} |\n\n")

        f.write("---\n\n")

        f.write("## 3. Delivered Items\n\n")
        if deliverables:
            for d in deliverables:
                icon = "✅" if d["approved"] else "📄"
                f.write(f"- {icon} **{d['title']}** — {d.get('description', '')}\n")
                if d.get("file_path"):
                    f.write(f"  - File: `{d['file_path']}`\n")
        else:
            f.write("### Milestones\n\n")
            for m in milestones:
                icon = "✅" if m["status"] == "completed" else "⬜"
                f.write(f"- {icon} **{m['title']}** — Phase {m['phase']}\n")
                if m.get("deliverables"):
                    f.write(f"  - {m['deliverables']}\n")
        f.write("\n")

        f.write("---\n\n")

        f.write("## 4. QA Summary\n\n")
        f.write(f"- **Total Checkpoints:** {quality['total']}\n")
        f.write(f"- **Passed:** {quality['passed']}\n")
        f.write(f"- **Failed:** {quality['failed']}\n")
        f.write(f"- **Pending:** {quality['pending']}\n\n")

        if not qa_approved:
            f.write("### Failed/Pending Items\n\n")
            for c in quality["checkpoints"]:
                if not c["passed"]:
                    f.write(f"- ❌ {c['checkpoint_name']} — {c.get('notes', 'Pending')}\n")
            f.write("\n")

        f.write("---\n\n")

        f.write("## 5. Client Package Contents\n\n")
        f.write("1. **Project Completion Report** — This document\n")
        f.write("2. **Deliverables** — All completed project deliverables\n")
        f.write("3. **QA Report** — Quality assurance test results\n")
        f.write("4. **Documentation** — User guides, technical docs\n")
        f.write("5. **Handover Notes** — Post-delivery support and maintenance\n\n")

        f.write("---\n\n")

        f.write("## 6. Post-Delivery Actions\n\n")
        f.write("1. Send delivery notification to client\n")
        f.write("2. Schedule project closeout meeting\n")
        f.write("3. Collect client feedback and satisfaction survey\n")
        f.write("4. Process final payment/invoice\n")
        f.write("5. Archive project documentation\n")
        f.write("6. Record lessons learned\n")
