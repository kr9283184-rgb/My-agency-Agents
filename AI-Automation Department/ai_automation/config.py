import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    OUTPUT_DIR = os.getenv("AUTOMATION_OUTPUT_DIR", "output")
    DB_PATH = os.getenv("AUTOMATION_DB_PATH", os.path.join(OUTPUT_DIR, "ai_automation.db"))
    PM_DB_PATH = os.getenv("PM_DB_PATH", "../Project-Management-Department/output/pm.db")

    DEFAULT_PROJECT_TYPE = os.getenv("AUTOMATION_DEFAULT_PROJECT_TYPE", "workflow_automation")
    DEFAULT_STACK = [
        item.strip()
        for item in os.getenv("AUTOMATION_DEFAULT_STACK", "langgraph,n8n,postgresql").split(",")
        if item.strip()
    ]

    @classmethod
    def pm_db_exists(cls) -> bool:
        return os.path.isfile(cls.PM_DB_PATH)
