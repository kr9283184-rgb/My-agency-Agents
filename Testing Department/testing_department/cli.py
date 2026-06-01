import argparse
import json
import os
import sys

from testing_department.config import Config
from testing_department.database import TestingDatabase
from testing_department.orchestrator import TestingOrchestrator


def main():
    parser = argparse.ArgumentParser(
        description="Quality Assurance & Testing Department",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  qa-test --project qa_project.json\n"
            "  qa-test --product \"Client Portal\" --type web_application --risk high\n"
            "  qa-test --status\n"
        ),
    )
    parser.add_argument("--project", default="", help="Path to JSON QA project file")
    parser.add_argument("--product", default="", help="Product name")
    parser.add_argument("--type", default=Config.DEFAULT_PRODUCT_TYPE, help="Product type")
    parser.add_argument("--risk", default=Config.DEFAULT_RISK_LEVEL, help="low, medium, high, or critical")
    parser.add_argument("--owner", default="", help="Responsible owner")
    parser.add_argument("--requirements", default="", help="Product requirements")
    parser.add_argument("--acceptance", default="", help="Acceptance criteria")
    parser.add_argument("--output", default=Config.OUTPUT_DIR, help="Output directory")
    parser.add_argument("--db", default=Config.DB_PATH, help="Testing department SQLite database")
    parser.add_argument("--status", action="store_true", help="Show testing department status")
    parser.add_argument("--id", default="", help="Specific QA project ID for status")

    args = parser.parse_args()

    db = TestingDatabase(args.db)
    orchestrator = TestingOrchestrator(db=db)

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
            print(f"Error reading QA project file: {e}")
            sys.exit(1)

    product = args.product or "Demo Product"
    qa_id = product.lower().replace(" ", "_").replace("-", "_")
    return {
        "qa_id": qa_id,
        "product_name": product,
        "product_type": args.type,
        "risk_level": args.risk,
        "owner": args.owner,
        "requirements": args.requirements,
        "acceptance_criteria": args.acceptance,
    }


def _print_status(status: dict):
    print("\n" + "=" * 60)
    print("  TESTING DEPARTMENT STATUS")
    print("=" * 60)
    if "error" in status:
        print(f"\n  Error: {status['error']}\n")
        return
    if "project" in status:
        item = status["project"]
        print(f"\n  Product: {item.get('product_name', '')}")
        print(f"  Status: {item.get('status', '')}")
        print(f"  Decision: {item.get('qa_decision', '')}")
        print(f"  Quality Score: {item.get('quality_score', 0)}")
        print(f"  Outputs: {len(status.get('outputs', []))}")
        print(f"  Bugs: {len(status.get('bugs', []))}")
    else:
        summary = status.get("summary", {})
        print(f"\n  Total Projects: {summary.get('total_projects', 0)}")
        print(f"  Average Quality Score: {summary.get('average_quality_score', 0)}")
        for decision, count in summary.get("by_decision", {}).items():
            print(f"  {decision}: {count}")
        source_dbs = status.get("source_dbs", {})
        if source_dbs:
            print("\n  Source Databases:")
            for name, exists in source_dbs.items():
                print(f"    {name}: {'found' if exists else 'not found'}")
    print()


def _print_result(result):
    summary = result.summary()
    print("\n" + "=" * 60)
    print("  QA REVIEW COMPLETE")
    print("=" * 60)
    print(f"\n  Total projects processed: {summary['total_projects']}")
    print(f"  Successfully completed: {summary['completed']}")
    print(f"  Failed: {summary['failed']}")
    for report in result.reports:
        if report["status"] == "completed":
            print(f"\n  Generated QA reports for {report['product']}:")
            for artifact in report.get("outputs", {}).values():
                if artifact.get("file_path"):
                    print(f"    {artifact['file_path']}")
    print()


if __name__ == "__main__":
    main()
