import argparse
import json
import os
import sys

from website_development.config import Config
from website_development.database import WebsiteDatabase
from website_development.orchestrator import WebsiteOrchestrator


def main():
    parser = argparse.ArgumentParser(
        description="AI Website Development & Design Department",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  website-develop --project project.json\n"
            "  website-develop --company \"Acme Dental\" --type dental_clinic --platform wordpress\n"
            "  website-develop --status\n"
        ),
    )
    parser.add_argument("--project", default="", help="Path to JSON project file")
    parser.add_argument("--company", default="", help="Company/client name")
    parser.add_argument("--type", default=Config.DEFAULT_PROJECT_TYPE, help="Website specialization type")
    parser.add_argument("--platform", default=Config.DEFAULT_PLATFORM, help="static, react, nextjs, wordpress, or shopify")
    parser.add_argument("--industry", default="", help="Client industry")
    parser.add_argument("--output", default=Config.OUTPUT_DIR, help="Output directory")
    parser.add_argument("--db", default=Config.DB_PATH, help="Website department SQLite database")
    parser.add_argument("--status", action="store_true", help="Show website department status")
    parser.add_argument("--id", default="", help="Specific project ID for status")

    args = parser.parse_args()

    db = WebsiteDatabase(args.db)
    orchestrator = WebsiteOrchestrator(db=db)

    if args.status:
        _print_status(orchestrator.run_status(args.id))
        return

    project = _load_project(args)
    result = orchestrator.run(project=project, output_dir=os.path.abspath(args.output))
    _print_result(result)


def _load_project(args) -> dict:
    if args.project:
        try:
            with open(args.project) as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("Project file must contain a JSON object")
            return data
        except (OSError, json.JSONDecodeError, ValueError) as e:
            print(f"Error reading project file: {e}")
            sys.exit(1)

    company = args.company or "Demo Client"
    project_id = company.lower().replace(" ", "_").replace("-", "_")
    return {
        "project_id": project_id,
        "company_name": company,
        "industry": args.industry,
        "project_type": args.type,
        "platform": args.platform,
    }


def _print_status(status: dict):
    print("\n" + "=" * 60)
    print("  WEBSITE DEVELOPMENT STATUS")
    print("=" * 60)
    if "error" in status:
        print(f"\n  Error: {status['error']}\n")
        return
    if "project" in status:
        p = status["project"]
        print(f"\n  Project: {p.get('company_name', '')}")
        print(f"  Status: {p.get('status', '')}")
        print(f"  Completion: {p.get('completion_pct', 0)}%")
        print(f"  Outputs: {len(status.get('outputs', []))}")
    else:
        summary = status.get("summary", {})
        print(f"\n  Total Projects: {summary.get('total_projects', 0)}")
        for stage, count in summary.get("by_status", {}).items():
            print(f"  {stage}: {count}")
    print()


def _print_result(result):
    summary = result.summary()
    print("\n" + "=" * 60)
    print("  WEBSITE DEVELOPMENT COMPLETE")
    print("=" * 60)
    print(f"\n  Total projects processed: {summary['total_projects']}")
    print(f"  Successfully executed: {summary['executed']}")
    print(f"  Failed: {summary['failed']}")
    for report in result.reports:
        if report["status"] == "completed":
            print(f"\n  Generated deliverables for {report['company']}:")
            for artifact in report.get("outputs", {}).values():
                if artifact.get("file_path"):
                    print(f"    {artifact['file_path']}")
    print()


if __name__ == "__main__":
    main()
