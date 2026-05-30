import os
from onboarding_department.agents.base_agent import BaseAgent


class AccessAgent(BaseAgent):
    def track_access(self, lead: dict, output_dir: str = "") -> dict:
        company = lead.get("company_name", "")
        contact = lead.get("contact_name", "")

        file_path = ""
        if output_dir:
            company_dir = os.path.join(output_dir, company.replace(" ", "_"))
            os.makedirs(company_dir, exist_ok=True)
            file_path = os.path.join(company_dir, "05_access_checklist.md")
            with open(file_path, "w") as f:
                self._write_access_checklist(f, company, contact)
            self.log(f"Access checklist saved to {file_path}")

        return {"file_path": file_path, "status": "generated"}

    def _write_access_checklist(self, f, company: str, contact: str):
        f.write(f"# Access & Credentials Checklist — {company}\n\n")
        f.write(f"**Client:** {contact}\n")
        f.write(f"**Company:** {company}\n\n")

        f.write("> **IMPORTANT:** Never share credentials in this document. \n")
        f.write("> Use this checklist to track what access is needed and its status.\n\n")
        f.write("---\n\n")

        f.write("## Hosting & Infrastructure\n\n")
        f.write("| Service | Access Needed | Status | Owner | Notes |\n")
        f.write("|---------|--------------|--------|-------|-------|\n")
        f.write("| Hosting Provider | Yes/No | Pending/Requested/Granted | Client/Vendor | \n")
        f.write("| Domain Registrar | Yes/No | Pending/Requested/Granted | Client/Vendor | \n")
        f.write("| SSL Certificate | Yes/No | Pending/Requested/Granted | Client/Vendor | \n")
        f.write("| CDN (Cloudflare, etc.) | Yes/No | Pending/Requested/Granted | Client/Vendor | \n")
        f.write("| DNS Management | Yes/No | Pending/Requested/Granted | Client/Vendor | \n\n")

        f.write("## Content Management\n\n")
        f.write("| System | Access Needed | Status | Owner | Notes |\n")
        f.write("|--------|--------------|--------|-------|-------|\n")
        f.write("| CMS (WordPress, etc.) | Yes/No | Pending/Requested/Granted | Client | \n")
        f.write("| Page Builder | Yes/No | Pending/Requested/Granted | Client | \n")
        f.write("| E-commerce Platform | Yes/No | Pending/Requested/Granted | Client | \n\n")

        f.write("## Analytics & Tracking\n\n")
        f.write("| Service | Access Needed | Status | Owner | Notes |\n")
        f.write("|---------|--------------|--------|-------|-------|\n")
        f.write("| Google Analytics | Yes/No | Pending/Requested/Granted | Client | \n")
        f.write("| Google Search Console | Yes/No | Pending/Requested/Granted | Client | \n")
        f.write("| Google Tag Manager | Yes/No | Pending/Requested/Granted | Client | \n")
        f.write("| Facebook Pixel | Yes/No | Pending/Requested/Granted | Client | \n")
        f.write("| Hotjar / Session Recording | Yes/No | Pending/Requested/Granted | Client | \n\n")

        f.write("## Email & Communication\n\n")
        f.write("| Service | Access Needed | Status | Owner | Notes |\n")
        f.write("|---------|--------------|--------|-------|-------|\n")
        f.write("| Email Hosting | Yes/No | Pending/Requested/Granted | Client | \n")
        f.write("| Mailchimp / Email Marketing | Yes/No | Pending/Requested/Granted | Client | \n")
        f.write("| SMTP Credentials | Yes/No | Pending/Requested/Granted | Client | \n\n")

        f.write("## Social Media\n\n")
        f.write("| Platform | Access Needed | Status | Owner | Notes |\n")
        f.write("|----------|--------------|--------|-------|-------|\n")
        f.write("| Facebook / Instagram | Yes/No | Pending/Requested/Granted | Client | \n")
        f.write("| LinkedIn | Yes/No | Pending/Requested/Granted | Client | \n")
        f.write("| Twitter / X | Yes/No | Pending/Requested/Granted | Client | \n")
        f.write("| YouTube | Yes/No | Pending/Requested/Granted | Client | \n")
        f.write("| TikTok | Yes/No | Pending/Requested/Granted | Client | \n\n")

        f.write("## Development & Design\n\n")
        f.write("| Service | Access Needed | Status | Owner | Notes |\n")
        f.write("|---------|--------------|--------|-------|-------|\n")
        f.write("| GitHub / Git Repository | Yes/No | Pending/Requested/Granted | Client | \n")
        f.write("| Design Files (Figma, etc.) | Yes/No | Pending/Requested/Granted | Client | \n")
        f.write("| Staging Environment | Yes/No | Pending/Requested/Granted | Vendor | \n")
        f.write("| FTP / SFTP Access | Yes/No | Pending/Requested/Granted | Client | \n")
        f.write("| Database Access | Yes/No | Pending/Requested/Granted | Client | \n\n")

        f.write("## Third-Party Integrations\n\n")
        f.write("| Service | Access Needed | Status | Owner | Notes |\n")
        f.write("|---------|--------------|--------|-------|-------|\n")
        f.write("| CRM (HubSpot, Salesforce) | Yes/No | Pending/Requested/Granted | Client | \n")
        f.write("| Payment Gateway (Stripe, PayPal) | Yes/No | Pending/Requested/Granted | Client | \n")
        f.write("| Accounting Software | Yes/No | Pending/Requested/Granted | Client | \n")
        f.write("| Booking System | Yes/No | Pending/Requested/Granted | Client | \n")
        f.write("| Other APIs | Yes/No | Pending/Requested/Granted | Client | \n\n")

        f.write("---\n\n")
        f.write("## Access Status Summary\n\n")
        f.write("**Total Services Tracked:** 30+\n")
        f.write("**Access Requested:** \n")
        f.write("**Access Granted:** \n")
        f.write("**Pending:** \n\n")
        f.write("**Ownership:** \n")
        f.write("- **Client-Owned:** Services the client controls\n")
        f.write("- **Vendor-Owned:** Services we provision\n\n")

        f.write("**Instructions:**\n")
        f.write("1. Mark each service with Yes/No for whether access is needed\n")
        f.write("2. Update status as access is requested and granted\n")
        f.write("3. Store actual credentials in a secure password manager (never in this document)\n")
        f.write("4. Note any special instructions or limitations\n")
