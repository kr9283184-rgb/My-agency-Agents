import os
from onboarding_department.agents.base_agent import BaseAgent


class AssetAgent(BaseAgent):
    def collect_assets(self, lead: dict, output_dir: str = "") -> dict:
        company = lead.get("company_name", "")
        contact = lead.get("contact_name", "")
        proposal_type = lead.get("proposal_type", "service")

        file_path = ""
        if output_dir:
            company_dir = os.path.join(output_dir, company.replace(" ", "_"))
            os.makedirs(company_dir, exist_ok=True)
            file_path = os.path.join(company_dir, "04_asset_request_form.md")
            with open(file_path, "w") as f:
                self._write_asset_request(f, company, contact, proposal_type)
            self.log(f"Asset request form saved to {file_path}")

        return {"file_path": file_path, "status": "generated"}

    def _write_asset_request(self, f, company: str, contact: str, proposal_type: str):
        f.write(f"# Asset Collection Request — {company}\n\n")
        f.write(f"**Client:** {contact}\n")
        f.write(f"**Company:** {company}\n")
        f.write(f"**Project Type:** {proposal_type}\n\n")
        f.write("---\n\n")

        f.write("## Required Assets\n\n")
        f.write("Please provide the following assets to help us get started:\n\n")

        f.write("### 1. Logo & Branding\n\n")
        f.write("- [ ] Primary Logo (vector format: AI, EPS, or SVG preferred)\n")
        f.write("- [ ] Secondary Logo / Alternate versions\n")
        f.write("- [ ] Favicon / Icon\n")
        f.write("- [ ] Brand Style Guide / Brand Guidelines (if available)\n")
        f.write("- [ ] Color Palette (hex codes)\n")
        f.write("- [ ] Typography / Font specifications\n\n")

        f.write("### 2. Images & Graphics\n\n")
        f.write("- [ ] Hero/Banner images (high resolution, 1920px+ wide)\n")
        f.write("- [ ] Team/Staff photos\n")
        f.write("- [ ] Product/Service photos\n")
        f.write("- [ ] Office/Location photos\n")
        f.write("- [ ] Background textures or patterns\n")
        f.write("- [ ] Icons or illustrations\n\n")

        f.write("### 3. Video & Media\n\n")
        f.write("- [ ] Brand video / promotional video\n")
        f.write("- [ ] Product demos or tutorials\n")
        f.write("- [ ] Client testimonials (video)\n")
        f.write("- [ ] Podcast episodes or audio assets\n\n")

        f.write("### 4. Content & Copy\n\n")
        f.write("- [ ] About Us page content\n")
        f.write("- [ ] Service/Product descriptions\n")
        f.write("- [ ] Company history / Story\n")
        f.write("- [ ] Team biographies\n")
        f.write("- [ ] Existing blog posts or articles\n")
        f.write("- [ ] Testimonials and reviews\n")
        f.write("- [ ] FAQ content\n\n")

        f.write("### 5. Marketing Materials\n\n")
        f.write("- [ ] Brochures or catalogs (PDF)\n")
        f.write("- [ ] Existing email templates\n")
        f.write("- [ ] Social media profiles and content\n")
        f.write("- [ ] Advertising creatives\n\n")

        f.write("### 6. Technical Assets\n\n")
        f.write("- [ ] Existing website files (if redesign)\n")
        f.write("- [ ] Database exports or backups\n")
        f.write("- [ ] API documentation\n")
        f.write("- [ ] Third-party integration details\n\n")

        f.write("---\n\n")
        f.write("## Submission Instructions\n\n")
        f.write("1. Review the checklist above and mark items as you gather them\n")
        f.write("2. Upload assets to a shared folder (Google Drive, Dropbox, etc.)\n")
        f.write("3. Share the folder link with your onboarding team\n")
        f.write("4. For large files, use a cloud storage service\n")
        f.write("5. If you don't have certain assets, note it — we can work with what's available\n\n")

        f.write("## Asset Quality Guidelines\n\n")
        f.write("- Images should be at least 1920px wide for hero/background use\n")
        f.write("- Logos should be in vector format when possible\n")
        f.write("- Avoid heavily compressed JPEGs for primary images\n")
        f.write("- Name files descriptively (e.g., `company-logo.png` not `img001.jpg`)\n")

        f.write("\n---\n")
        f.write("*Please return this form along with your assets to your onboarding team.*\n")
