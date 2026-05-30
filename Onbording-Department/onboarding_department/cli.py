import os
import argparse
from onboarding_department.config import Config
from onboarding_department.database import OnboardingDatabase
from onboarding_department.orchestrator import OnboardingOrchestrator


def main():
    parser = argparse.ArgumentParser(
        description="AI Client Onboarding Department — Multi-agent onboarding system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  onboarding --db ./output/outreach.db
  onboarding --db ./output/outreach.db --lead lead-001
  onboarding --db ./output/outreach.db --output ./onboarding
  onboarding --status
  onboarding --status --lead lead-001
        """,
    )

    parser.add_argument(
        "--db",
        default=Config.OUTREACH_DB_PATH,
        help="Path to client-outreach SQLite database (default: OUTREACH_DB_PATH env var)",
    )
    parser.add_argument(
        "--lead",
        default="",
        help="Onboard a specific lead by ID (default: all won leads)",
    )
    parser.add_argument(
        "--output",
        default=Config.OUTPUT_DIR,
        help="Output directory for generated documents (default: ONBOARDING_OUTPUT_DIR env var)",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show onboarding pipeline status instead of running",
    )

    args = parser.parse_args()

    os.environ["OUTREACH_DB_PATH"] = args.db
    os.environ["ONBOARDING_OUTPUT_DIR"] = args.output

    db = OnboardingDatabase()
    orchestrator = OnboardingOrchestrator(db=db)

    if args.status:
        status = orchestrator.run_status(args.lead)
        _print_status(status)
    else:
        output_dir = os.path.abspath(args.output)
        result = orchestrator.run(lead_id=args.lead, output_dir=output_dir)
        _print_result(result)


def _print_status(status: dict):
    print("\n" + "=" * 60)
    print("  ONBOARDING PIPELINE STATUS")
    print("=" * 60)

    outreach = status.get("outreach_db", {})
    if "error" in outreach:
        print(f"\n  Outreach DB: {outreach['error']}")
    else:
        stages = outreach.get("stages", {})
        print("\n  Outreach Pipeline:")
        for stage, count in sorted(stages.items()):
            print(f"    {stage}: {count}")

    leads = status.get("leads", [])
    if leads:
        print("\n  Onboarding Progress:")
        for l in leads:
            bar_len = 20
            filled = int((l.get("stage_index", 0) / max(l.get("total_stages", 1), 1)) * bar_len)
            bar = "█" * filled + "░" * (bar_len - filled)
            print(f"    {l.get('company', l.get('lead_id', '')):30s} {bar} {l.get('current_stage', '')}")

    print()


def _print_result(result):
    summary = result.summary()
    print("\n" + "=" * 60)
    print("  ONBOARDING COMPLETE")
    print("=" * 60)
    print(f"\n  Total leads processed: {summary['total_leads']}")
    print(f"  Successfully onboarded: {summary['onboarded']}")
    print(f"  Failed: {summary['failed']}")

    if result.reports:
        print("\n  Report files:")
        for r in result.reports:
            if r["status"] == "completed":
                outputs = r.get("outputs", {})
                for key, val in outputs.items():
                    if isinstance(val, dict) and val.get("file_path"):
                        print(f"    {val['file_path']}")

    print()


if __name__ == "__main__":
    main()
