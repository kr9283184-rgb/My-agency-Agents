import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    OUTPUT_DIR = os.getenv("SECURITY_OUTPUT_DIR", "output")
    DB_PATH = os.getenv("SECURITY_DB_PATH", os.path.join(OUTPUT_DIR, "security_department.db"))

    PM_DB_PATH = os.getenv("PM_DB_PATH", "../Project-Management-Department/output/pm.db")
    WEBSITE_DB_PATH = os.getenv("WEBSITE_DB_PATH", "../WEB-Devlopement Department/output/website_development.db")
    AUTOMATION_DB_PATH = os.getenv("AUTOMATION_DB_PATH", "../AI-Automation Department/output/ai_automation.db")

    DEFAULT_ASSESSMENT_TYPE = os.getenv("SECURITY_DEFAULT_ASSESSMENT_TYPE", "security_review")
    DEFAULT_RISK_LEVEL = os.getenv("SECURITY_DEFAULT_RISK_LEVEL", "medium")

    @classmethod
    def source_dbs(cls) -> dict:
        return {
            "project_management": cls.PM_DB_PATH,
            "website_development": cls.WEBSITE_DB_PATH,
            "ai_automation": cls.AUTOMATION_DB_PATH,
        }

    @classmethod
    def source_db_status(cls) -> dict:
        return {name: os.path.isfile(path) for name, path in cls.source_dbs().items()}
