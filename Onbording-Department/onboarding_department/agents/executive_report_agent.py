import os
from datetime import datetime
from typing import Optional
from onboarding_department.agents.base_agent import BaseAgent


class ExecutiveReportAgent(BaseAgent):
    def generate_report(self, lead: dict, onboarding_results: dict, output_dir: str = "") -> dict:
        company = lead.get("company_name", "")
        contact = lead.get("contact_name", "")
        lead_id = lead.get("lead_id", "")

        file_path = ""
        if output_dir:
            company_dir = os.path.join(output_dir, company.replace(" ", "_"))
            os.makedirs(company_dir, exist_ok=True)
            file_path = os.path.join(company_dir, "11_executive_onboarding_report.md")
            with open(file_path, "w") as f:
                self._write_report(f, lead, onboarding_results)
            self.log(f"Executive report saved to {file_path}")

        return {"file_path": file_path}

    def _write_report(self, f, lead: dict, results: dict):
        company = lead.get("company_name", "")
        contact = lead.get("contact_name", "")
        email = lead.get("email", "")
        industry = lead.get("industry", "")
        proposal_type = lead.get("proposal_type", "service")
        deal_amount = lead.get("deal_amount", 0)
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        f.write("=" * 60 + "\n")
        f.write(f"  EXECUTIVE ONBOARDING REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"  Generated: {now}\n")
        f.write(f"  Status: Onboarding Complete\n\n")
        f.write("=" * 60 + "\n\n")

        f.write("## Client Information\n\n")
        f.write(f"- **Company:** {company}\n")
        f.write(f"- **Contact:** {contact}\n")
        f.write(f"- **Email:** {email}\n")
        f.write(f"- **Industry:** {industry}\n")
        f.write(f"- **Project Type:** {proposal_type}\n")
        f.write(f"- **Deal Value:** ${float(deal_amount):,.2f}\n\n")

        f.write("---\n\n")

        f.write("## Onboarding Summary\n\n")

        welcome = results.get("welcome", {})
        f.write(f"- **Welcome Sent:** {'Yes' if welcome.get('email_sent') or welcome.get('whatsapp_sent') else 'No'}\n")
        f.write(f"  - Email: {'Sent' if welcome.get('email_sent') else 'N/A'}\n")
        f.write(f"  - WhatsApp: {'Sent' if welcome.get('whatsapp_sent') else 'N/A'}\n")

        questionnaire = results.get("questionnaire", {})
        f.write(f"- **Questionnaire:** {'Generated' if questionnaire.get('file_path') else 'Pending'}\n")

        requirements = results.get("requirements", {})
        f.write(f"- **Requirements Collected:** {'Yes' if requirements.get('file_path') else 'No'}\n")

        assets = results.get("assets", {})
        f.write(f"- **Asset Request Sent:** {'Yes' if assets.get('file_path') else 'No'}\n")

        brand = results.get("brand", {})
        f.write(f"- **Brand Analysis:** {'Complete' if brand.get('file_path') else 'Pending'}\n")

        scope = results.get("scope", {})
        f.write(f"- **Scope Defined:** {'Yes' if scope.get('file_path') else 'No'}\n")

        contract = results.get("contract", {}).get("details", {})
        f.write(f"- **Contract Verified:** {'Yes' if contract.get('agreement_signed') else 'Pending'}\n")

        roadmap = results.get("roadmap", {})
        f.write(f"- **Roadmap Created:** {'Yes' if roadmap.get('file_path') else 'No'}\n")

        handover = results.get("handover", {})
        f.write(f"- **Handover Complete:** {'Yes' if handover.get('file_path') else 'No'}\n")
        f.write(f"- **Handed Over To:** {handover.get('destination_department', 'TBD')}\n\n")

        f.write("---\n\n")

        f.write("## Generated Documents\n\n")
        doc_map = {
            "welcome": "Welcome Package",
            "questionnaire": "Client Questionnaire",
            "requirements": "Client Requirement Document",
            "assets": "Asset Request Form",
            "access": "Access Checklist",
            "brand": "Brand Analysis Report",
            "scope": "Project Scope Document",
            "contract": "Contract Verification",
            "roadmap": "Project Roadmap",
            "handover": "Development Handover Package",
            "report": "Executive Onboarding Report",
        }
        for key, label in doc_map.items():
            item = results.get(key, {})
            fp = item.get("file_path", "") if isinstance(item, dict) else ""
            status = "✅" if fp else "⏳"
            f.write(f"- {status} {label}\n")

        f.write("\n---\n\n")

        f.write("## Pipeline Progress\n\n")
        f.write("```\n")
        f.write("Lead → Qualified → Proposal Sent → Won → ")
        f.write("Onboarding → Planning → Production → Testing → Completed\n")
        f.write("                               ↑\n")
        f.write("                    You are here (Onboarding Complete)\n")
        f.write("```\n\n")

        f.write("---\n\n")

        f.write("## Next Steps\n\n")
        f.write("1. Production team reviews handover package\n")
        f.write("2. Schedule kickoff meeting with development team\n")
        f.write("3. Begin Phase 1: Research & Discovery\n")
        f.write("4. Regular status updates to client\n\n")

        f.write("=" * 60 + "\n")
        f.write(f"  END OF REPORT — {company.upper()}\n")
        f.write("=" * 60 + "\n")
