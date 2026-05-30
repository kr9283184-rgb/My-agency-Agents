import os
from onboarding_department.agents.base_agent import BaseAgent


class BrandAgent(BaseAgent):
    def analyze_brand(self, lead: dict, output_dir: str = "") -> dict:
        company = lead.get("company_name", "")
        industry = lead.get("industry", "")
        website = lead.get("website", "")
        notes = lead.get("notes", "")

        summary, competitor_analysis, design_recs = self._analyze(
            company, industry, website, notes
        )

        file_path = ""
        if output_dir:
            company_dir = os.path.join(output_dir, company.replace(" ", "_"))
            os.makedirs(company_dir, exist_ok=True)
            file_path = os.path.join(company_dir, "06_brand_analysis_report.md")
            with open(file_path, "w") as f:
                self._write_report(f, company, industry, summary, competitor_analysis, design_recs)
            self.log(f"Brand analysis report saved to {file_path}")

        return {
            "file_path": file_path,
            "summary": summary,
            "competitor_analysis": competitor_analysis,
            "design_recommendations": design_recs,
        }

    def _analyze(self, company: str, industry: str, website: str, notes: str) -> tuple:
        brand_type = self._infer_brand_type(industry)
        competitors = self._get_competitors(industry)
        design_style = self._get_design_style(industry)

        summary = f"{company} operates in the {industry} industry. "
        summary += f"Brand positioning suggests a {brand_type} market approach. "
        summary += "The brand should communicate trust, professionalism, and industry expertise."

        competitor_analysis = (
            f"Key competitors in the {industry} space include: "
        )
        for comp in competitors[:3]:
            competitor_analysis += f"\n- **{comp}**: A direct competitor in this space"

        design_recs = (
            f"Design recommendations for {industry} brand:\n"
            f"- Style: {design_style}\n"
            f"- Color palette: Blues and whites for trust and professionalism\n"
            f"- Typography: Clean, modern sans-serif fonts\n"
            f"- Imagery: Professional photography showing real people and results\n"
            f"- Voice: Professional yet approachable"
        )

        return summary, competitor_analysis, design_recs

    def _infer_brand_type(self, industry: str) -> str:
        types = {
            "real estate": "local service",
            "healthcare": "trust-based",
            "technology": "innovative",
            "education": "authoritative",
            "ecommerce": "consumer-focused",
            "legal": "trust-based",
            "finance": "trust-based",
            "hospitality": "experience-focused",
        }
        return types.get(industry.lower(), "professional service")

    def _get_competitors(self, industry: str) -> list:
        competitors = {
            "real estate": ["Zillow", "Realtor.com", "Redfin"],
            "healthcare": ["WebMD", "Healthline", "Mayo Clinic"],
            "technology": ["TechCrunch", "CNET", "The Verge"],
            "education": ["Coursera", "Udemy", "Khan Academy"],
            "ecommerce": ["Amazon", "Shopify", "BigCommerce"],
            "legal": ["LegalZoom", "Rocket Lawyer", "Avvo"],
            "finance": ["Bloomberg", "Yahoo Finance", "NerdWallet"],
            "hospitality": ["Booking.com", "Expedia", "TripAdvisor"],
        }
        return competitors.get(industry.lower(), ["Industry leaders in this space"])

    def _get_design_style(self, industry: str) -> str:
        styles = {
            "real estate": "Clean, professional with warm tones and high-quality imagery",
            "healthcare": "Clean, calming, trustworthy with soft blues and greens",
            "technology": "Modern, minimalist with bold colors and dynamic layouts",
            "education": "Clean, accessible with warm colors and clear typography",
            "ecommerce": "Clean, conversion-focused with prominent CTAs",
            "legal": "Professional, authoritative with conservative colors",
            "finance": "Clean, professional with blues and trust signals",
            "hospitality": "Luxurious, immersive with high-quality visuals",
        }
        return styles.get(industry.lower(), "Modern, professional design")

    def _write_report(self, f, company: str, industry: str, summary: str,
                      competitor_analysis: str, design_recs: str):
        f.write(f"# Brand Analysis Report — {company}\n\n")
        f.write(f"**Industry:** {industry}\n")
        f.write(f"**Analysis Date:** Generated during onboarding\n\n")
        f.write("---\n\n")

        f.write("## Brand Summary\n\n")
        f.write(summary)
        f.write("\n\n---\n\n")

        f.write("## Competitor Analysis\n\n")
        f.write(competitor_analysis)
        f.write("\n\n---\n\n")

        f.write("## Market Positioning\n\n")
        f.write(f"- **Industry:** {industry}\n")
        f.write(f"- **Brand Type:** {self._infer_brand_type(industry)}\n")
        f.write("- **Target Audience:** Businesses and consumers in this space\n")
        f.write("- **Value Proposition:** Quality service and professional expertise\n\n")

        f.write("---\n\n")

        f.write("## Design Recommendations\n\n")
        f.write(design_recs)
        f.write("\n\n---\n\n")

        f.write("## Brand Identity Checklist\n\n")
        f.write("- [ ] Logo usage guidelines established\n")
        f.write("- [ ] Color palette defined\n")
        f.write("- [ ] Typography selected\n")
        f.write("- [ ] Brand voice documented\n")
        f.write("- [ ] Imagery style defined\n")
        f.write("- [ ] Brand messaging framework created\n")
