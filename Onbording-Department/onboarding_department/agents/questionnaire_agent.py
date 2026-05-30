import os
from onboarding_department.agents.base_agent import BaseAgent


class QuestionnaireAgent(BaseAgent):
    def generate_questionnaire(self, lead: dict, output_dir: str = "") -> dict:
        company = lead.get("company_name", "")
        contact = lead.get("contact_name", "")
        industry = lead.get("industry", "")

        file_path = ""
        if output_dir:
            company_dir = os.path.join(output_dir, company.replace(" ", "_"))
            os.makedirs(company_dir, exist_ok=True)
            file_path = os.path.join(company_dir, "03_questionnaire.md")
            with open(file_path, "w") as f:
                self._write_questionnaire(f, company, contact, industry)
            self.log(f"Questionnaire saved to {file_path}")

        return {"file_path": file_path, "status": "generated"}

    def _write_questionnaire(self, f, company: str, contact: str, industry: str):
        f.write(f"# Client Onboarding Questionnaire — {company}\n\n")
        f.write(f"**Prepared for:** {contact}\n")
        f.write(f"**Company:** {company}\n")
        f.write(f"**Industry:** {industry}\n\n")
        f.write("---\n\n")

        f.write("## Section 1: Company Information\n\n")
        f.write("1. What is your company's mission and vision?\n")
        f.write("   \n\n")
        f.write("2. How long has your company been in business?\n")
        f.write("   \n\n")
        f.write("3. How many employees does your company have?\n")
        f.write("   \n\n")
        f.write("4. What is your primary business model? (B2B, B2C, Both)\n")
        f.write("   \n\n")

        f.write("## Section 2: Branding Details\n\n")
        f.write("5. Do you have existing brand guidelines? (If yes, please share)\n")
        f.write("   \n\n")
        f.write("6. Describe your brand voice (e.g., professional, casual, playful, authoritative)\n")
        f.write("   \n\n")
        f.write("7. What colors best represent your brand?\n")
        f.write("   \n\n")
        f.write("8. Who are your main competitors?\n")
        f.write("   \n\n")

        f.write("## Section 3: Business Goals\n\n")
        f.write("9. What are your top 3 business goals for the next 12 months?\n")
        f.write("   \n\n")
        f.write("10. How do you measure success for this project?\n")
        f.write("    \n\n")
        f.write("11. What specific problems are you trying to solve?\n")
        f.write("    \n\n")

        f.write("## Section 4: Feature Requests\n\n")
        f.write("12. List any specific features or functionality you need:\n")
        f.write("    \n\n")
        f.write("13. Are there any integrations required? (CRM, analytics, payment gateways, etc.)\n")
        f.write("    \n\n")
        f.write("14. Do you need mobile responsiveness?\n")
        f.write("    \n\n")

        f.write("## Section 5: Budget & Timeline\n\n")
        f.write("15. What is your estimated budget range for this project?\n")
        f.write("    \n\n")
        f.write("16. What is your desired launch date?\n")
        f.write("    \n\n")
        f.write("17. Are there any critical deadlines or events we should know about?\n")
        f.write("    \n\n")

        f.write("## Section 6: Additional Information\n\n")
        f.write("18. Any additional notes or requirements you'd like to share?\n")
        f.write("    \n\n")
        f.write("19. Who are the key stakeholders we should communicate with?\n")
        f.write("    \n\n")
        f.write("20. Preferred communication frequency? (Daily, Weekly, As needed)\n")
        f.write("    \n\n")

        f.write("---\n")
        f.write("*Please fill out this questionnaire and return it to your onboarding team.*\n")
