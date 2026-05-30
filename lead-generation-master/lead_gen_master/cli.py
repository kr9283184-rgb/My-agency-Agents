import argparse
import sys

from lead_gen_master.orchestrator import Orchestrator


def main():
    parser = argparse.ArgumentParser(
        description="AI Lead Generation Master",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  lead-gen-master --industry \"real estate\" --location \"Austin, TX\"\n"
            "  lead-gen-master -i dentists -l \"Miami, FL\" --max-leads 50\n"
            "  lead-gen-master --research-only\n"
        ),
    )
    parser.add_argument(
        "-i", "--industry",
        default=None,
        help="Target industry (default: from .env or 'real estate agents')",
    )
    parser.add_argument(
        "-l", "--location",
        default=None,
        help="Target location (default: from .env or 'Austin, TX')",
    )
    parser.add_argument(
        "-m", "--max-leads",
        type=int,
        default=None,
        help="Maximum leads to collect (default: 25)",
    )
    parser.add_argument(
        "-o", "--output-dir",
        default=None,
        help="Output directory for reports (default: ./output)",
    )
    parser.add_argument(
        "--research-only",
        action="store_true",
        help="Only run business research (skip enrichment/audit)",
    )

    args = parser.parse_args()

    orc = Orchestrator(
        target_industry=args.industry,
        target_location=args.location,
        max_leads=args.max_leads or 25,
        output_dir=args.output_dir,
    )

    if args.research_only:
        leads = orc.run_research_only()
        print(f"\nFound {len(leads)} leads.")
        sys.exit(0)

    result = orc.run()

    s = result.summary()
    print(f"\nResults:")
    print(f"  Leads:      {s['total_leads']}")
    print(f"  Qualified:  {s['qualified_leads']}")
    print(f"  High Pri:   {s['high_priority']}")
    print(f"  Report:     {s['report_path']}")


if __name__ == "__main__":
    main()
