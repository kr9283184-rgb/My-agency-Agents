import os
import json
import argparse
from project_management.config import Config
from project_management.database import ProjectDatabase
from project_management.orchestrator import ProjectOrchestrator


def main():
    parser = argparse.ArgumentParser(
        description="AI Project Management Department — Multi-agent project management system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  project-manage
  project-manage --project project-001
  project-manage --onboarding-db ../Onbording-Department/output/onboarding.db
  project-manage --output ./pm_output
  project-manage --status
  project-manage --status --project project-001
  project-manage --weekly --project project-001
  project-manage --monthly
  project-manage --change-request '{"title":"Add Analytics","description":"Integrate Google Analytics","estimated_hours":8}'
    """,
    )

    parser.add_argument(
        "--onboarding-db",
        default=Config.ONBOARDING_DB_PATH,
        help="Path to onboarding SQLite database (default: ONBOARDING_DB_PATH env var)",
    )
    parser.add_argument(
        "--project",
        default="",
        help="Manage a specific project by ID (default: all projects)",
    )
    parser.add_argument(
        "--output",
        default=Config.OUTPUT_DIR,
        help="Output directory for generated reports (default: PM_OUTPUT_DIR env var)",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show project status instead of running full management",
    )
    parser.add_argument(
        "--weekly",
        action="store_true",
        help="Generate weekly progress report",
    )
    parser.add_argument(
        "--monthly",
        action="store_true",
        help="Generate monthly executive report",
    )
    parser.add_argument(
        "--change-request",
        default="",
        help="JSON string with change request data for a project",
    )

    args = parser.parse_args()

    if args.onboarding_db:
        os.environ["ONBOARDING_DB_PATH"] = args.onboarding_db
    if args.output:
        os.environ["PM_OUTPUT_DIR"] = args.output

    db = ProjectDatabase()
    orchestrator = ProjectOrchestrator(db=db)

    if args.status:
        status = orchestrator.run_status(args.project)
        _print_status(status)
    elif args.weekly:
        if args.project:
            result = orchestrator.run_weekly_report(args.project, os.path.abspath(args.output))
            _print_report_result(result, "Weekly")
        else:
            parser.error("--weekly requires --project")
    elif args.monthly:
        result = orchestrator.run_monthly_executive(os.path.abspath(args.output))
        _print_executive_result(result)
    elif args.change_request:
        if not args.project:
            parser.error("--change-request requires --project")
        try:
            cr_data = json.loads(args.change_request)
        except json.JSONDecodeError:
            parser.error("--change-request must be valid JSON")
        result = orchestrator.process_change_request(args.project, cr_data, os.path.abspath(args.output))
        _print_cr_result(result)
    else:
        output_dir = os.path.abspath(args.output)
        result = orchestrator.run(project_id=args.project, output_dir=output_dir)
        _print_result(result)


def _print_status(status: dict):
    print("\n" + "=" * 60)
    print("  PROJECT STATUS")
    print("=" * 60)

    if "error" in status:
        print(f"\n  Error: {status['error']}")
        print()
        return

    if "project" in status:
        p = status["project"]
        print(f"\n  Project: {p.get('company', p.get('project_id', ''))}")
        print(f"  Status: {p.get('status', 'unknown')}")
        print(f"  Completion: {p.get('completion_pct', 0)}%")
        print(f"  Tasks: {p.get('tasks_completed', '?')}")
        print(f"  Open Risks: {p.get('open_risks', 0)}")
        print(f"  Budget: {p.get('budget_health', 'unknown')}")
        print(f"  Margin: {p.get('profit_margin', '?')}")
    elif "projects" in status:
        print(f"\n  Portfolio Health:")
        portfolio = status.get("portfolio", {})
        print(f"    Total: {portfolio.get('total_projects', 0)}")
        print(f"    On Track: {portfolio.get('on_track', 0)}")
        print(f"    Completed: {portfolio.get('completed', 0)}")
        print(f"    Delayed: {portfolio.get('delayed', 0)}")
        print(f"    Budget Health: {portfolio.get('budget_health', 'unknown')}")
        print()

        for p in status["projects"]:
            bar_len = 20
            filled = int((p.get("completion_pct", 0) / 100) * bar_len)
            bar = "█" * filled + "░" * (bar_len - filled)
            print(f"  {p['company']:30s} {bar} {p['status']:15s} {p.get('completion_pct', 0):5.1f}%")

    print()


def _print_result(result):
    summary = result.summary()
    print("\n" + "=" * 60)
    print("  PROJECT MANAGEMENT COMPLETE")
    print("=" * 60)
    print(f"\n  Total projects processed: {summary['total_projects']}")
    print(f"  Successfully executed: {summary['executed']}")
    print(f"  Failed: {summary['failed']}")

    if result.reports:
        print("\n  Generated reports:")
        for r in result.reports:
            if r["status"] == "completed":
                outputs = r.get("outputs", {})
                for key, val in outputs.items():
                    if isinstance(val, dict) and val.get("file_path"):
                        print(f"    {val['file_path']}")

    print()


def _print_report_result(result, report_type):
    print(f"\n{'='*60}")
    print(f"  {report_type} REPORT GENERATED")
    print(f"{'='*60}")
    if isinstance(result, dict) and result.get("file_path"):
        print(f"\n  Report: {result['file_path']}")
        print(f"  Completion: {result.get('completion_pct', 0):.1f}%")
    print()


def _print_executive_result(result):
    print(f"\n{'='*60}")
    print("  MONTHLY EXECUTIVE REPORT")
    print(f"{'='*60}")

    portfolio = result.get("portfolio_health", {})
    print(f"\n  Portfolio Health:")
    print(f"    Total Projects: {portfolio.get('total_projects', 0)}")
    print(f"    On Track: {portfolio.get('on_track', 0)}")
    print(f"    Completed: {portfolio.get('completed', 0)}")
    print(f"    Delayed: {portfolio.get('delayed', 0)}")

    summary = result.get("project_summary", {})
    print(f"\n  Project Summary:")
    print(f"    Total: {summary.get('total_projects', 0)}")
    for status, count in summary.get("by_status", {}).items():
        print(f"    {status}: {count}")

    print()


def _print_cr_result(result):
    print(f"\n{'='*60}")
    print("  CHANGE REQUEST PROCESSED")
    print(f"{'='*60}")
    if "error" in result:
        print(f"\n  Error: {result['error']}")
    else:
        cr = result.get("change_request", {})
        print(f"\n  Title: {cr.get('title', 'N/A')}")
        print(f"  Status: {cr.get('status', 'pending')}")
        print(f"  Effort: {result.get('impact', {}).get('effort_hours', 0)} hours")
        print(f"  Timeline Impact: {result.get('impact', {}).get('timeline_days', 0)} days")
        print(f"  Cost Impact: ${result.get('impact', {}).get('cost', 0):,.2f}")
        if result.get("file_path"):
            print(f"  Report: {result['file_path']}")
    print()


if __name__ == "__main__":
    main()
