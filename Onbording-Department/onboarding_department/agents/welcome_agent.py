import os
from typing import Optional
from onboarding_department.agents.base_agent import BaseAgent
from onboarding_department.email.smtp_sender import SMTPSender
from onboarding_department.email.templates import WELCOME_EMAIL_TEMPLATE, PROJECT_KICKOFF_EMAIL_TEMPLATE
from onboarding_department.browser.whatsapp import WhatsAppAutomation


class WelcomeAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sender = SMTPSender()
        self.whatsapp = WhatsAppAutomation()

    def send_welcome_package(self, lead: dict, output_dir: str = "") -> dict:
        lead_id = lead.get("lead_id", "")
        company = lead.get("company_name", "")
        contact = lead.get("contact_name", "there")
        email = lead.get("email", "")
        phone = lead.get("whatsapp_phone", "")

        email_sent = False
        whatsapp_sent = False
        file_path = ""

        email_body = WELCOME_EMAIL_TEMPLATE.format(
            contact_name=contact,
            company_name=company,
            from_email=self.sender.from_email,
            from_name=self.sender.from_name,
        )

        if email and self.sender.is_configured():
            subject = f"Welcome to {company} — Your Onboarding Has Started!"
            email_sent = self.sender.send(to=email, subject=subject, body=email_body)
            if email_sent:
                self.log(f"Welcome email sent to {email}")
        elif email:
            self.log(f"SMTP not configured, welcome email for {email} simulated")
            email_sent = True  # Simulated as sent

        if phone:
            params = {"contact_name": contact, "company_name": company}
            whatsapp_sent = self.whatsapp.send_template(phone, "welcome", params)
            if whatsapp_sent:
                self.log(f"Welcome WhatsApp sent to {phone}")
        else:
            self.log(f"No WhatsApp number for {lead_id}")

        if output_dir:
            company_dir = os.path.join(output_dir, company.replace(" ", "_"))
            os.makedirs(company_dir, exist_ok=True)
            file_path = os.path.join(company_dir, "01_welcome_package.md")
            with open(file_path, "w") as f:
                f.write(f"# Welcome Package — {company}\n\n")
                f.write(f"**Client:** {contact}\n")
                f.write(f"**Company:** {company}\n")
                f.write(f"**Email:** {email}\n")
                f.write(f"**WhatsApp:** {phone}\n\n")
                f.write("---\n\n")
                f.write("## Welcome Email\n\n")
                f.write(email_body)
                f.write("\n\n---\n\n")
                f.write("## Next Steps\n\n")
                f.write("1. Complete the onboarding questionnaire\n")
                f.write("2. Share brand assets (logo, images, guidelines)\n")
                f.write("3. Review and approve project scope\n")
                f.write("4. Project moves to production\n\n")
                f.write("## Contact Information\n\n")
                f.write(f"- Email: {self.sender.from_email}\n")
                f.write(f"- Team: {self.sender.from_name}\n")
                f.write("- Response Time: Within 24 hours\n")

        return {
            "status": "sent" if (email_sent or not email) else "failed",
            "email_sent": email_sent,
            "whatsapp_sent": whatsapp_sent,
            "file_path": file_path,
        }
