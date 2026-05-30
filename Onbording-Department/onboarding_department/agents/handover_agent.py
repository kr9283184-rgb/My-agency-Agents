import os
from typing import Optional
from onboarding_department.agents.base_agent import BaseAgent


class HandoverAgent(BaseAgent):
    def prepare_handover(self, lead: dict, onboarding_results: dict, output_dir: str = "") -> dict:
        company = lead.get("company_name", "")
        contact = lead.get("contact_name", "")
        lead_id = lead.get("lead_id", "")

        outputs = self.db.get_outputs(lead_id) if lead_id else []
        file_path = ""

        if output_dir:
            company_dir = os.path.join(output_dir, company.replace(" ", "_"))
            os.makedirs(company_dir, exist_ok=True)
            file_path = os.path.join(company_dir, "10_development_handover_package.md")
            with open(file_path, "w") as f:
                self._write_handover(f, lead, onboarding_results, outputs)
            self.log(f"Handover package saved to {file_path}")

        return {
            "file_path": file_path,
            "destination_department": self._get_destination(lead),
        }

    def _get_destination(self, lead: dict) -> str:
        proposal_type = lead.get("proposal_type", "service")
        mapping = {
            "website": "Website Development Department",
            "automation": "AI Automation Department",
            "seo": "Marketing Department",
        }
        return mapping.get(proposal_type, "Development Department")

    def _write_handover(self, f, lead: dict, results: dict, outputs: list):
        company = lead.get("company_name", "")
        contact = lead.get("contact_name", "")
        email = lead.get("email", "")
        phone = lead.get("whatsapp_phone", "")
        industry = lead.get("industry", "")
        proposal_type = lead.get("proposal_type", "service")
        deal_amount = lead.get("deal_amount", 0)

        f.write(f"# Development Handover Package — {company}\n\n")
        f.write("---\n\n")

        f.write("## 1. Client Summary\n\n")
        f.write(f"- **Company:** {company}\n")
        f.write(f"- **Contact:** {contact}\n")
        f.write(f"- **Email:** {email}\n")
        f.write(f"- **Phone/WhatsApp:** {phone}\n")
        f.write(f"- **Industry:** {industry}\n")
        f.write(f"- **Project Type:** {proposal_type}\n")
        f.write(f"- **Deal Value:** ${float(deal_amount):,.2f}\n")
        f.write(f"- **Status:** Ready for Production\n")
        f.write(f"- **Handover To:** {self._get_destination(lead)}\n\n")

        f.write("---\n\n")

        f.write("## 2. Requirements Summary\n\n")
        reqs = results.get("requirements", {}).get("details", {})
        if reqs:
            f.write(f"- **Business Goals:** {reqs.get('business_goals', 'See requirements doc')}\n")
            f.write(f"- **Target Audience:** {reqs.get('target_audience', '')}\n")
            f.write(f"- **Style Preferences:** {reqs.get('preferred_style', '')}\n")
            f.write(f"- **Required Pages/Features:** See requirements document\n\n")
        else:
            f.write("See client requirement document for full details.\n\n")

        f.write("---\n\n")

        f.write("## 3. Assets Package\n\n")
        asset_form = results.get("assets", {}).get("file_path", "")
        contract = results.get("contract", {}).get("details", {})
        if contract:
            f.write(f"- **Agreement Status:** {'Signed' if contract.get('agreement_signed') else 'Pending'}\n")
            f.write(f"- **Payment Status:** {contract.get('payment_status', 'Pending').title()}\n")
        f.write(f"\n**Asset request form:** `{asset_form}`\n\n")

        f.write("---\n\n")

        f.write("## 4. Access Checklist\n\n")
        access_file = results.get("access", {}).get("file_path", "")
        f.write(f"- **Access checklist:** `{access_file}`\n")
        f.write("- All necessary access should be requested before development begins.\n\n")

        f.write("---\n\n")

        f.write("## 5. Timeline\n\n")
        f.write("| Phase | Duration |\n")
        f.write("|-------|----------|\n")
        f.write("| Research & Discovery | Weeks 1-2 |\n")
        f.write("| Design | Weeks 3-4 |\n")
        f.write("| Development | Weeks 5-8 |\n")
        f.write("| Testing & QA | Week 9 |\n")
        f.write("| Launch | Week 10 |\n\n")

        f.write("---\n\n")

        f.write("## 6. Priority Notes\n\n")
        f.write("- **Urgency:** Normal\n")
        f.write("- **Key Contact:** Client prefers email communication\n")
        f.write("- **Project Kickoff:** Scheduled with the production team\n")
        f.write("- **Dependencies:** Asset collection in progress\n\n")

        f.write("---\n\n")

        f.write("## 7. Generated Documents\n\n")
        for output in outputs:
            f.write(f"- [{output['output_type'].title()}] {output.get('file_path', '')}\n")
        f.write("\n---\n\n")

        f.write("## 8. Recommended Actions\n\n")
        f.write("1. Review all onboarding documents before contacting the client\n")
        f.write("2. Schedule kickoff meeting with the production team\n")
        f.write("3. Assign project lead and development resources\n")
        f.write("4. Set up project management workspace\n")
        f.write("5. Begin Phase 1: Research & Discovery\n")
