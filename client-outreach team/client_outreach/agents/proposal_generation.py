import os
from datetime import datetime
from typing import Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable,
)
from reportlab.lib import colors

from client_outreach.agents.base_agent import BaseAgent
from client_outreach.llm.base import LLMProvider


class ProposalGenerationAgent(BaseAgent):
    def __init__(self, llm: Optional[LLMProvider] = None, output_dir: str = "output", **kwargs):
        super().__init__(**kwargs)
        self.llm = llm
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_service_proposal(self, lead: dict) -> Optional[str]:
        return self._generate_proposal(lead, "service")

    def generate_website_proposal(self, lead: dict) -> Optional[str]:
        return self._generate_proposal(lead, "website")

    def generate_seo_proposal(self, lead: dict) -> Optional[str]:
        return self._generate_proposal(lead, "seo")

    def generate_automation_proposal(self, lead: dict) -> Optional[str]:
        return self._generate_proposal(lead, "automation")

    def _generate_proposal(self, lead: dict, proposal_type: str) -> Optional[str]:
        lead_id = lead.get("lead_id", "")
        company = lead.get("company_name", "Client")
        contact = lead.get("contact_name", "")

        filename = f"{proposal_type}_proposal_{lead_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        content = self._build_proposal_content(lead, proposal_type)
        self._render_pdf(filepath, company, content)

        proposal_id = self.db.add_proposal({
            "lead_id": lead_id,
            "title": f"{proposal_type.title()} Proposal — {company}",
            "proposal_type": proposal_type,
            "file_path": filepath,
            "amount": content.get("amount", 0),
            "status": "draft",
        })

        self.log(f"Generated {proposal_type} proposal: {filepath}")
        return filepath

    def _build_proposal_content(self, lead: dict, proposal_type: str) -> dict:
        if self.llm:
            prompt = (
                f"Generate a sales proposal for {lead.get('company_name', '')}, "
                f"a {lead.get('industry', '')} company. Proposal type: {proposal_type}.\n\n"
                f"Return a JSON object with:\n"
                f"- title: proposal title\n"
                f"- executive_summary: 2-3 paragraph executive summary\n"
                f"- services: list of services offered\n"
                f"- timeline: delivery timeline in weeks\n"
                f"- investment: total investment amount (number only)\n"
                f"- includes: list of what's included\n"
                f"- terms: payment terms"
            )
            result = self.llm.generate_json(prompt)
            import json
            try:
                content = json.loads(result)
                content["amount"] = float(content.get("investment", 0))
                return content
            except (json.JSONDecodeError, TypeError, ValueError):
                pass

        return self._default_proposal(lead, proposal_type)

    def _default_proposal(self, lead: dict, proposal_type: str) -> dict:
        base_amounts = {
            "service": 2500,
            "website": 5000,
            "seo": 1500,
            "automation": 3500,
        }
        amount = base_amounts.get(proposal_type, 2000)

        return {
            "title": f"{proposal_type.title()} Proposal",
            "executive_summary": (
                f"This proposal outlines how we will help "
                f"{lead.get('company_name', 'your company')} achieve their "
                f"growth objectives through our proven {proposal_type} solutions."
            ),
            "services": [
                f"Custom {proposal_type} strategy development",
                "Implementation and setup",
                "Training and onboarding",
                "Monthly performance reporting",
            ],
            "timeline": "4-6 weeks",
            "investment": amount,
            "amount": amount,
            "includes": [
                "Dedicated project manager",
                "Weekly progress updates",
                "30-day post-launch support",
            ],
            "terms": "50% upfront, 50% upon completion",
        }

    def _render_pdf(self, filepath: str, company: str, content: dict):
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
        )
        styles = getSampleStyleSheet()
        style_normal = styles["Normal"]
        style_heading = styles["Heading1"]
        style_heading2 = styles["Heading2"]

        accent = HexColor("#1a237e")

        elements = []

        elements.append(Paragraph(f"Proposal for {company}", style_heading))
        elements.append(Spacer(1, 0.25*inch))

        elements.append(Paragraph(content.get("executive_summary", ""), style_normal))
        elements.append(Spacer(1, 0.25*inch))

        elements.append(Paragraph("Services", style_heading2))
        for service in content.get("services", []):
            elements.append(Paragraph(f"• {service}", style_normal))
        elements.append(Spacer(1, 0.2*inch))

        elements.append(Paragraph("Timeline", style_heading2))
        elements.append(Paragraph(content.get("timeline", "4-6 weeks"), style_normal))
        elements.append(Spacer(1, 0.2*inch))

        elements.append(Paragraph("Investment", style_heading2))
        amount = content.get("investment", 0)
        elements.append(Paragraph(f"${amount:,.2f}", style_normal))
        elements.append(Spacer(1, 0.2*inch))

        elements.append(Paragraph("What's Included", style_heading2))
        for item in content.get("includes", []):
            elements.append(Paragraph(f"• {item}", style_normal))
        elements.append(Spacer(1, 0.2*inch))

        elements.append(Paragraph("Terms", style_heading2))
        elements.append(Paragraph(content.get("terms", "50% upfront, 50% upon completion"), style_normal))

        doc.build(elements)

    def send_proposal(self, lead: dict, proposal_type: str = "service") -> Optional[str]:
        filepath = self._generate_proposal(lead, proposal_type)
        if filepath:
            self.db.update_pipeline_stage(lead.get("lead_id", ""), "Proposal Sent")
            self.log(f"Proposal ready to send to {lead.get('company_name', '')}: {filepath}")
        return filepath
