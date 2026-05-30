from typing import Optional
from datetime import datetime, timedelta

from client_outreach.agents.base_agent import BaseAgent
from client_outreach.llm.base import LLMProvider


class ExecutiveReportingAgent(BaseAgent):
    def __init__(self, llm: Optional[LLMProvider] = None, **kwargs):
        super().__init__(**kwargs)
        self.llm = llm

    def generate_daily_report(self, date_str: Optional[str] = None) -> str:
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        stats = self.db.get_daily_stats(date_str)

        report = []
        report.append("=" * 60)
        report.append(f"  DAILY SALES REPORT — {date_str}")
        report.append("=" * 60)
        report.append(f"  Leads Contacted:    {stats['leads_contacted']}")
        report.append(f"  Emails Sent:        {stats['emails_sent']}")
        report.append(f"  Messages Sent:      {stats['messages_sent']}")
        report.append(f"  Replies Received:   {stats['replies_received']}")
        report.append(f"  Meetings Booked:    {stats['meetings_booked']}")
        report.append(f"  Proposals Sent:     {stats['proposals_sent']}")
        report.append(f"  Deals Closed:       {stats['deals_closed']}")
        report.append(f"  Revenue Generated:  ${stats['revenue_generated']:,.2f}")
        report.append("=" * 60)

        report_text = "\n".join(report)
        print(report_text)
        return report_text

    def generate_weekly_report(self) -> str:
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())

        total_leads = 0
        total_emails = 0
        total_messages = 0
        total_replies = 0
        total_meetings = 0
        total_proposals = 0
        total_deals = 0
        total_revenue = 0.0

        for i in range(7):
            day = start_of_week + timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            stats = self.db.get_daily_stats(day_str)
            total_leads += stats["leads_contacted"]
            total_emails += stats["emails_sent"]
            total_messages += stats["messages_sent"]
            total_replies += stats["replies_received"]
            total_meetings += stats["meetings_booked"]
            total_proposals += stats["proposals_sent"]
            total_deals += stats["deals_closed"]
            total_revenue += stats["revenue_generated"]

        summary = self.db.summary()
        pipeline = summary.get("pipeline", {})
        best_channel = self._best_performing_channel()
        conversion_rate = self._conversion_rate()

        report = []
        report.append("=" * 60)
        report.append(f"  WEEKLY SALES REPORT — {start_of_week.strftime('%b %d')} – {today.strftime('%b %d, %Y')}")
        report.append("=" * 60)
        report.append("")
        report.append("  📊 PERFORMANCE")
        report.append(f"  Leads Contacted:    {total_leads}")
        report.append(f"  Emails Sent:        {total_emails}")
        report.append(f"  Messages Sent:      {total_messages}")
        report.append(f"  Replies Received:   {total_replies}")
        report.append(f"  Meetings Booked:    {total_meetings}")
        report.append(f"  Proposals Sent:     {total_proposals}")
        report.append(f"  Deals Closed:       {total_deals}")
        report.append(f"  Revenue Generated:  ${total_revenue:,.2f}")
        report.append("")
        report.append("  📈 PIPELINE HEALTH")
        for stage, count in pipeline.items():
            report.append(f"  {stage}: {count}")
        report.append("")
        report.append(f"  🏆 Best Channel:     {best_channel}")
        report.append(f"  📉 Conversion Rate:  {conversion_rate:.1f}%")
        report.append(f"  📊 Revenue Forecast: ${total_revenue * 1.3:,.2f}")
        report.append("=" * 60)

        report_text = "\n".join(report)
        print(report_text)
        return report_text

    def _best_performing_channel(self) -> str:
        conn = self.db._get_conn()
        try:
            row = conn.execute("""
                SELECT channel, COUNT(*) as replies
                FROM communications
                WHERE direction = 'inbound'
                GROUP BY channel
                ORDER BY replies DESC
                LIMIT 1
            """).fetchone()
            return row["channel"] if row else "N/A"
        finally:
            conn.close()

    def _conversion_rate(self) -> float:
        conn = self.db._get_conn()
        try:
            total = conn.execute(
                "SELECT COUNT(*) FROM leads"
            ).fetchone()[0] or 0
            won = conn.execute(
                "SELECT COUNT(*) FROM leads WHERE pipeline_stage = 'Won'"
            ).fetchone()[0] or 0
            if total == 0:
                return 0.0
            return (won / total) * 100
        finally:
            conn.close()
