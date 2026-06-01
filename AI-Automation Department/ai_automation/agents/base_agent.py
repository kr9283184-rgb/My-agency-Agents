import os
from typing import Optional

from ai_automation.database import AutomationDatabase


class BaseAgent:
    def __init__(self, db: Optional[AutomationDatabase] = None):
        self.db = db or AutomationDatabase()
        self.name = self.__class__.__name__

    def log(self, message: str):
        print(f"[{self.name}] {message}")

    def _project_dir(self, project: dict, output_dir: str) -> str:
        company = project.get("company_name", "automation_project").replace(" ", "_")
        path = os.path.join(output_dir, company)
        os.makedirs(path, exist_ok=True)
        return path

    def _write_markdown(self, project: dict, output_dir: str, filename: str, title: str, sections: dict) -> dict:
        project_dir = self._project_dir(project, output_dir)
        file_path = os.path.join(project_dir, filename)
        company = project.get("company_name", "Unknown")
        with open(file_path, "w") as f:
            f.write(f"# {title} - {company}\n\n")
            f.write(f"- **Project ID:** {project.get('project_id', '')}\n")
            f.write(f"- **Industry:** {project.get('industry', '')}\n")
            f.write(f"- **Project Type:** {project.get('project_type', project.get('proposal_type', 'workflow_automation'))}\n")
            f.write(f"- **Priority:** {project.get('priority', 'medium')}\n")
            f.write(f"- **Timeline:** {project.get('timeline', '')}\n\n")
            for heading, items in sections.items():
                f.write(f"## {heading}\n\n")
                if isinstance(items, list):
                    for item in items:
                        f.write(f"- {item}\n")
                else:
                    f.write(f"{items}\n")
                f.write("\n")
        return {"file_path": file_path, "title": title, "status": "created"}
