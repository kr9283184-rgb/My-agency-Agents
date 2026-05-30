import json
import re
from typing import Optional
from lead_gen_master.agents.base_agent import BaseAgent
from lead_gen_master.llm.base import LLMProvider


class ExecutiveReportAgent(BaseAgent):
    def __init__(
        self,
        llm: Optional[LLMProvider] = None,
        memory=None,
    ):
        super().__init__(memory)
        self.llm = llm

    def generate(
        self,
        leads: list[dict],
        audits: Optional[list[dict]] = None,
        briefs: Optional[list[dict]] = None,
    ) -> str:
        self.log("Generating executive report")

        total = len(leads)
        qualified = [l for l in leads if l.get("lead_score", 0) >= 50]
        high = [l for l in leads if l.get("priority") == "High"]

        stats = self._compute_stats(leads)

        if self.llm and self.llm.is_available():
            narrative = self._llm_narrative(
                total, qualified, high, stats
            )
        else:
            narrative = self._template_narrative(
                total, qualified, high, stats
            )

        report = (
            f"{'='*60}\n"
            f"  DAILY EXECUTIVE REPORT\n"
            f"  Generated: {__import__('datetime', fromlist=['datetime']).datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"{'='*60}\n\n"
            f"SUMMARY\n"
            f"  Total Leads Found:     {total}\n"
            f"  Total Qualified:       {len(qualified)}\n"
            f"  High Priority:         {len(high)}\n"
            f"  Top Industry:          {stats['top_industry']}\n"
            f"  Avg Lead Score:        {stats['avg_score']:.1f}\n\n"
            f"NARRATIVE\n{narrative}\n\n"
            f"TOP OPPORTUNITIES\n"
        )

        for lead in high[:5]:
            report += (
                f"  - {lead.get('company_name', 'Unknown')} "
                f"(Score: {lead.get('lead_score', 0)}) "
                f"[{lead.get('recommended_service', '')}]\n"
            )

        report += (
            f"\nRECOMMENDED ACTIONS\n"
            f"  1. Prioritize outreach to high-priority leads\n"
            f"  2. Follow up on website audit findings\n"
            f"  3. Focus on {stats['top_industry']} sector\n"
            f"  4. Prepare customized proposals for top 5 leads\n"
        )

        return report

    def _compute_stats(self, leads: list[dict]) -> dict:
        from collections import Counter

        industries = [
            l.get("industry", "Unknown")
            for l in leads
            if l.get("industry")
        ]
        scores = [l.get("lead_score", 0) for l in leads]

        return {
            "top_industry": (
                Counter(industries).most_common(1)[0][0]
                if industries
                else "N/A"
            ),
            "avg_score": (
                sum(scores) / len(scores) if scores else 0
            ),
        }

    def _llm_narrative(
        self,
        total: int,
        qualified: list,
        high: list,
        stats: dict,
    ) -> str:
        prompt = (
            f"Write a brief executive narrative (2-3 paragraphs) "
            f"summarizing today's lead generation results:\n"
            f"- {total} total leads found\n"
            f"- {len(qualified)} qualified (score >= 50)\n"
            f"- {len(high)} high priority\n"
            f"- Top industry: {stats['top_industry']}\n"
            f"- Average lead score: {stats['avg_score']:.1f}\n\n"
            f"Tone: professional, actionable. "
            f"Focus on opportunities and next steps."
        )
        return self.llm.generate(
            prompt, temperature=0.5, max_tokens=500
        )

    def _template_narrative(
        self,
        total: int,
        qualified: list,
        high: list,
        stats: dict,
    ) -> str:
        return (
            f"The team identified {total} potential leads today, "
            f"with {len(qualified)} meeting qualification criteria "
            f"(score >= 50) and {len(high)} designated as high priority. "
            f"The {stats['top_industry']} sector showed the strongest "
            f"opportunity, averaging a score of {stats['avg_score']:.1f}. "
            f"Immediate follow-up is recommended for high-priority leads "
            f"to capitalize on current market conditions."
        )
