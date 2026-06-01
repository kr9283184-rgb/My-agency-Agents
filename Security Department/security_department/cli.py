import argparse
import json
import os
import sys

from security_department.config import Config
from security_department.database import SecurityDatabase
from security_department.orchestrator import SecurityOrchestrator


def main():
    parser = argparse.ArgumentParser(
        description="Cybersecurity & System Reliability Department",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  security-department --assessment assessment.json\n"
            "  security-department --target \"Client Portal\" --type web_application --risk high\n"
            "  security-department --status\n"
        ),
    )
    parser.add_argument("--assessment", default="", help="Path to JSON assessment file")
    parser.add_argument("--target", default="", help="Target system, app, client, or department")
    parser.add_argument("--type", default="system", help="Target type, such as web_application, api, ai_system, infrastructure")
    parser.add_argument("--assessment-type", default=Config.DEFAULT_ASSESSMENT_TYPE, help="Assessment type")
    parser.add_argument("--risk", default=Config.DEFAULT_RISK_LEVEL, help="low, medium, high, or critical")
    parser.add_argument("--owner", default="", help="Responsible owner")
    parser.add_argument("--scope", default="", help="Assessment scope")
    parser.add_argument("--output", default=Config.OUTPUT_DIR, help="Output directory")
    parser.add_argument("--db", default=Config.DB_PATH, help="Security department SQLite database")
    parser.add_argument("--status", action="store_true", help="Show security department status")
    parser.add_argument("--id", default="", help="Specific assessment ID for status")

    args = parser.parse_args()

    db = SecurityDatabase(args.db)
    orchestrator = SecurityOrchestrator(db=db)

    if args.status:
        _print_status(orchestrator.run_status(args.id))
        return

    assessment = _load_assessment(args)
    result = orchestrator.run(assessment=assessment, output_dir=os.path.abspath(args.output))
    _print_result(result)


def _load_assessment(args) -> dict:
    if args.assessment:
        try:
            with open(args.assessment) as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("Assessment file must contain a JSON object")
            return data
        except (OSError, json.JSONDecodeError, ValueError) as e:
            print(f"Error reading assessment file: {e}")
            sys.exit(1)

    target = args.target or "Demo System"
    assessment_id = target.lower().replace(" ", "_").replace("-", "_")
    return {
        "assessment_id": assessment_id,
        "target_name": target,
        "target_type": args.type,
        "assessment_type": args.assessment_type,
        "risk_level": args.risk,
        "owner": args.owner,
        "scope": args.scope,
    }


def _print_status(status: dict):
    print("\n" + "=" * 60)
    print("  SECURITY DEPARTMENT STATUS")
    print("=" * 60)
    if "error" in status:
        print(f"\n  Error: {status['error']}\n")
        return
    if "assessment" in status:
        item = status["assessment"]
        print(f"\n  Target: {item.get('target_name', '')}")
        print(f"  Status: {item.get('status', '')}")
        print(f"  Risk: {item.get('risk_level', '')}")
        print(f"  Score: {item.get('security_score', 0)}")
        print(f"  Outputs: {len(status.get('outputs', []))}")
        print(f"  Vulnerabilities: {len(status.get('vulnerabilities', []))}")
    else:
        summary = status.get("summary", {})
        print(f"\n  Total Assessments: {summary.get('total_assessments', 0)}")
        print(f"  Average Security Score: {summary.get('average_security_score', 0)}")
        for stage, count in summary.get("by_status", {}).items():
            print(f"  {stage}: {count}")
        source_dbs = status.get("source_dbs", {})
        if source_dbs:
            print("\n  Source Databases:")
            for name, exists in source_dbs.items():
                print(f"    {name}: {'found' if exists else 'not found'}")
    print()


def _print_result(result):
    summary = result.summary()
    print("\n" + "=" * 60)
    print("  SECURITY ASSESSMENT COMPLETE")
    print("=" * 60)
    print(f"\n  Total assessments processed: {summary['total_assessments']}")
    print(f"  Successfully completed: {summary['completed']}")
    print(f"  Failed: {summary['failed']}")
    for report in result.reports:
        if report["status"] == "completed":
            print(f"\n  Generated reports for {report['target']}:")
            for artifact in report.get("outputs", {}).values():
                if artifact.get("file_path"):
                    print(f"    {artifact['file_path']}")
    print()


if __name__ == "__main__":
    main()
