import os
from typing import Optional

from testing_department.database import TestingDatabase


class BaseAgent:
    def __init__(self, db: Optional[TestingDatabase] = None):
        self.db = db or TestingDatabase()
        self.name = self.__class__.__name__

    def log(self, message: str):
        print(f"[{self.name}] {message}")

    def _project_dir(self, project: dict, output_dir: str) -> str:
        product = project.get("product_name", "qa_project").replace(" ", "_")
        path = os.path.join(output_dir, product)
        os.makedirs(path, exist_ok=True)
        return path

    def _write_markdown(self, project: dict, output_dir: str, filename: str, title: str, sections: dict) -> dict:
        project_dir = self._project_dir(project, output_dir)
        file_path = os.path.join(project_dir, filename)
        product = project.get("product_name", "Unknown")
        with open(file_path, "w") as f:
            f.write(f"# {title} - {product}\n\n")
            f.write(f"- **QA ID:** {project.get('qa_id', '')}\n")
            f.write(f"- **Product Type:** {project.get('product_type', 'web_application')}\n")
            f.write(f"- **Risk Level:** {project.get('risk_level', 'medium')}\n")
            f.write(f"- **Owner:** {project.get('owner', '')}\n\n")
            for heading, items in sections.items():
                f.write(f"## {heading}\n\n")
                if isinstance(items, list):
                    for item in items:
                        f.write(f"- {item}\n")
                else:
                    f.write(f"{items}\n")
                f.write("\n")
        return {"file_path": file_path, "title": title, "status": "created"}
