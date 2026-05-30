import argparse
import json
import sys

from client_outreach.orchestrator import Orchestrator
from client_outreach.database import OutreachDatabase


def main():
    parser = argparse.ArgumentParser(
        description="AI Sales & Outreach Department",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  client-outreach --leads leads.json\n"
            "  client-outreach --leads leads.json --output-dir ./reports\n"
            "  client-outreach --import-only --leads leads.json\n"
            "  client-outreach --research-only --leads leads.json\n"
            "  client-outreach --daily-report\n"
            "  client-outreach --weekly-report\n"
            "  client-outreach --pipeline\n"
        ),
    )
    parser.add_argument(
        "--leads",
        help="Path to JSON file containing leads array",
    )
    parser.add_argument(
        "-o", "--output-dir",
        default=None,
        help="Output directory for reports and proposals (default: ./output)",
    )
    parser.add_argument(
        "--import-only",
        action="store_true",
        help="Only import leads into CRM (skip outreach)",
    )
    parser.add_argument(
        "--research-only",
        action="store_true",
        help="Only research leads (skip outreach)",
    )
    parser.add_argument(
        "--daily-report",
        action="store_true",
        help="Generate daily report only",
    )
    parser.add_argument(
        "--weekly-report",
        action="store_true",
        help="Generate weekly report only",
    )
    parser.add_argument(
        "--pipeline",
        action="store_true",
        help="Show pipeline summary",
    )
    parser.add_argument(
        "--date",
        default=None,
        help="Date for daily report (YYYY-MM-DD, default: today)",
    )

    args = parser.parse_args()

    orc = Orchestrator(output_dir=args.output_dir)

    if args.daily_report:
        from client_outreach.agents.executive_report import ExecutiveReportingAgent
        reporter = ExecutiveReportingAgent(db=orc._db)
        reporter.generate_daily_report(args.date)
        sys.exit(0)

    if args.weekly_report:
        from client_outreach.agents.executive_report import ExecutiveReportingAgent
        reporter = ExecutiveReportingAgent(db=orc._db)
        reporter.generate_weekly_report()
        sys.exit(0)

    if args.pipeline:
        summary = orc.crm.get_pipeline_summary()
        print(f"\nPipeline Summary:")
        print(f"  Total Leads: {summary.get('total_leads', 0)}")
        for stage, count in summary.get('pipeline', {}).items():
            print(f"  {stage}: {count}")
        sys.exit(0)

    if not args.leads:
        parser.print_help()
        sys.exit(1)

    try:
        with open(args.leads) as f:
            leads = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading leads file: {e}")
        sys.exit(1)

    if not isinstance(leads, list):
        print("Leads file must contain a JSON array")
        sys.exit(1)

    if args.import_only:
        count = orc.import_leads_only(leads)
        print(f"Imported {count} leads into CRM")
        sys.exit(0)

    if args.research_only:
        orc.research_only(leads)
        print(f"Researched {len(leads)} leads")
        sys.exit(0)

    result = orc.run(leads)
    s = result.summary()
    for k, v in s.items():
        print(f"  {k.replace('_', ' ').title()}: {v}")


if __name__ == "__main__":
    main()
