import os
from typing import Optional

from security_department.database import SecurityDatabase


class BaseAgent:
    def __init__(self, db: Optional[SecurityDatabase] = None):
        self.db = db or SecurityDatabase()
        self.name = self.__class__.__name__

    def log(self, message: str):
        print(f"[{self.name}] {message}")

    def _assessment_dir(self, assessment: dict, output_dir: str) -> str:
        target = assessment.get("target_name", "security_assessment").replace(" ", "_")
        path = os.path.join(output_dir, target)
        os.makedirs(path, exist_ok=True)
        return path

    def _write_markdown(self, assessment: dict, output_dir: str, filename: str, title: str, sections: dict) -> dict:
        assessment_dir = self._assessment_dir(assessment, output_dir)
        file_path = os.path.join(assessment_dir, filename)
        target = assessment.get("target_name", "Unknown")
        with open(file_path, "w") as f:
            f.write(f"# {title} - {target}\n\n")
            f.write(f"- **Assessment ID:** {assessment.get('assessment_id', '')}\n")
            f.write(f"- **Target Type:** {assessment.get('target_type', 'system')}\n")
            f.write(f"- **Assessment Type:** {assessment.get('assessment_type', 'security_review')}\n")
            f.write(f"- **Risk Level:** {assessment.get('risk_level', 'medium')}\n")
            f.write(f"- **Owner:** {assessment.get('owner', '')}\n\n")
            for heading, items in sections.items():
                f.write(f"## {heading}\n\n")
                if isinstance(items, list):
                    for item in items:
                        f.write(f"- {item}\n")
                else:
                    f.write(f"{items}\n")
                f.write("\n")
        return {"file_path": file_path, "title": title, "status": "created"}
