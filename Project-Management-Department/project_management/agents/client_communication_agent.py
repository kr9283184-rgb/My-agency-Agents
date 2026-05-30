import os
from datetime import datetime
from typing import Optional
from project_management.agents.base_agent import BaseAgent


class ClientCommunicationAgent(BaseAgent):
    def generate_update(self, project: dict, update_type: str = "weekly", output_dir: str = "") -> dict:
        project_id = project.get("project_id", "")
        company = project.get("company_name", "")
        contact = project.get("contact_name", "Client")
        email = project.get("email", "")

        milestones = self.db.get_milestones(project_id)
        tasks = self.db.get_tasks(project_id)
        risks = self.db.get_risks(project_id, "open")

        completion = sum(1 for t in tasks if t["state"] == "completed")
        total = len(tasks)
        completion_pct = (completion / total * 100) if total > 0 else 0

        subject = self._generate_subject(company, update_type, completion_pct)
        body = self._generate_body(company, contact, update_type, milestones, tasks, risks, completion_pct, completion, total)

        comm = {
            "project_id": project_id,
            "comm_type": f"{update_type}_update",
            "channel": "email",
            "subject": subject,
            "body": body,
            "recipient": email,
            "status": "draft",
        }
        comm_id = self.db.add_communication(comm)

        file_path = ""
        if output_dir:
            company_dir = os.path.join(output_dir, company.replace(" ", "_"))
            os.makedirs(company_dir, exist_ok=True)
            file_path = os.path.join(company_dir, "09_client_communication.md")
            with open(file_path, "w") as f:
                f.write(f"# {subject}\n\n")
                f.write(body)

        self.log(f"{update_type.title()} update generated for {company}")

        return {
            "file_path": file_path,
            "comm_id": comm_id,
            "subject": subject,
            "body": body,
            "update_type": update_type,
            "recipient": email,
        }

    def generate_milestone_notification(self, project: dict, milestone: dict) -> dict:
        company = project.get("company_name", "")
        contact = project.get("contact_name", "Client")
        email = project.get("email", "")

        subject = f"🎉 Milestone Completed: {milestone['title']} — {company}"
        body = (
            f"Hi {contact},\n\n"
            f"We are pleased to inform you that the milestone **'{milestone['title']}'** "
            f"has been completed successfully.\n\n"
            f"**What was delivered:**\n"
            f"{milestone.get('deliverables', 'See attached documentation')}\n\n"
            f"**Next Steps:**\n"
            f"The project is moving to the next phase. We'll keep you updated on progress.\n\n"
            f"Best regards,\n"
            f"Project Management Team"
        )

        comm_id = self.db.add_communication({
            "project_id": project.get("project_id", ""),
            "comm_type": "milestone_update",
            "channel": "email",
            "subject": subject,
            "body": body,
            "recipient": email,
            "status": "draft",
        })

        return {"comm_id": comm_id, "subject": subject, "body": body}

    def generate_delay_notification(self, project: dict, delay_info: dict) -> dict:
        company = project.get("company_name", "")
        contact = project.get("contact_name", "Client")
        email = project.get("email", "")

        subject = f"⚠️ Project Update: Schedule Adjustment — {company}"
        body = (
            f"Hi {contact},\n\n"
            f"We want to keep you informed about a schedule adjustment for your project.\n\n"
            f"**Issue:** {delay_info.get('description', 'A task has been delayed')}\n"
            f"**Impact:** {delay_info.get('impact', 'Minor schedule adjustment needed')}\n"
            f"**New Timeline:** {delay_info.get('new_date', 'Being determined')}\n\n"
            f"**Our Response:**\n"
            f"{delay_info.get('mitigation', 'We are working to minimize the impact')}\n\n"
            f"We apologize for any inconvenience and appreciate your understanding.\n\n"
            f"Best regards,\n"
            f"Project Management Team"
        )

        comm_id = self.db.add_communication({
            "project_id": project.get("project_id", ""),
            "comm_type": "delay_notification",
            "channel": "email",
            "subject": subject,
            "body": body,
            "recipient": email,
            "status": "draft",
        })

        return {"comm_id": comm_id, "subject": subject, "body": body}

    def generate_delivery_notification(self, project: dict) -> dict:
        company = project.get("company_name", "")
        contact = project.get("contact_name", "Client")
        email = project.get("email", "")

        subject = f"✅ Project Delivered: {company}"
        body = (
            f"Hi {contact},\n\n"
            f"We are excited to inform you that your project has been completed and delivered!\n\n"
            f"**What was delivered:**\n"
            f"- All project requirements have been met\n"
            f"- QA testing has been passed\n"
            f"- Documentation has been prepared\n\n"
            f"**Next Steps:**\n"
            f"1. Review the delivered project\n"
            f"2. Provide final feedback within 7 days\n"
            f"3. Schedule a closeout meeting if needed\n\n"
            f"Thank you for choosing us!\n\n"
            f"Best regards,\n"
            f"Project Management Team"
        )

        comm_id = self.db.add_communication({
            "project_id": project.get("project_id", ""),
            "comm_type": "delivery_notification",
            "channel": "email",
            "subject": subject,
            "body": body,
            "recipient": email,
            "status": "draft",
        })

        return {"comm_id": comm_id, "subject": subject, "body": body}

    def _generate_subject(self, company: str, update_type: str, completion_pct: float) -> str:
        templates = {
            "weekly": f"📋 Weekly Project Update — {company} ({completion_pct:.0f}% Complete)",
            "milestone": f"🎯 Milestone Update — {company}",
            "delivery": f"✅ Delivery Notification — {company}",
            "delay": f"⚠️ Project Update — {company}",
        }
        return templates.get(update_type, f"Project Update — {company}")

    def _generate_body(self, company: str, contact: str, update_type: str,
                       milestones: list, tasks: list, risks: list,
                       completion_pct: float, completed: int, total: int) -> str:
        body_lines = [f"Hi {contact},\n"]

        if update_type == "weekly":
            body_lines.append(f"Here is your weekly update for **{company}**.\n")
        elif update_type == "milestone":
            body_lines.append(f"Here is your milestone update for **{company}**.\n")

        body_lines.append(f"**Overall Progress:** {completion_pct:.0f}%")
        bar_len = 20
        filled = int((completion_pct / 100) * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        body_lines.append(f"**Progress Bar:** {bar}")
        body_lines.append(f"**Tasks:** {completed}/{total} completed\n")

        active_milestones = [m for m in milestones if m["status"] != "completed"]
        if active_milestones:
            body_lines.append("**Current Milestones:**\n")
            for m in active_milestones[:3]:
                icon = {"in_progress": "🔄", "pending": "⬜", "delayed": "⚠️"}.get(m["status"], "⬜")
                body_lines.append(f"- {icon} {m['title']} ({m.get('completion_pct', 0)}%)")
            body_lines.append("")

        if risks:
            body_lines.append(f"**Open Risks:** {len(risks)}")
            for r in risks[:3]:
                body_lines.append(f"- ⚠️ {r['title']}")
            body_lines.append("")

        body_lines.append("**Next Steps:**")
        if update_type == "weekly":
            body_lines.append("- Continue with current development activities")
            body_lines.append("- Prepare for upcoming milestones")
            body_lines.append("- We will be in touch with any updates")
        else:
            body_lines.append("- Review the latest developments")
            body_lines.append("- Let us know if you have questions")
            body_lines.append("- We value your feedback\n")

        body_lines.append("Best regards,")
        body_lines.append("Project Management Team")

        return "\n".join(body_lines)
