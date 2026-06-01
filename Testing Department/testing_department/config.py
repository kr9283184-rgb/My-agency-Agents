import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    OUTPUT_DIR = os.getenv("TESTING_OUTPUT_DIR", "output")
    DB_PATH = os.getenv("TESTING_DB_PATH", os.path.join(OUTPUT_DIR, "testing_department.db"))

    WEBSITE_DB_PATH = os.getenv("WEBSITE_DB_PATH", "../WEB-Devlopement Department/output/website_development.db")
    AUTOMATION_DB_PATH = os.getenv("AUTOMATION_DB_PATH", "../AI-Automation Department/output/ai_automation.db")
    SECURITY_DB_PATH = os.getenv("SECURITY_DB_PATH", "../Security Department/output/security_department.db")

    DEFAULT_PRODUCT_TYPE = os.getenv("TESTING_DEFAULT_PRODUCT_TYPE", "web_application")
    DEFAULT_RISK_LEVEL = os.getenv("TESTING_DEFAULT_RISK_LEVEL", "medium")

    @classmethod
    def source_dbs(cls) -> dict:
        return {
            "website_development": cls.WEBSITE_DB_PATH,
            "ai_automation": cls.AUTOMATION_DB_PATH,
            "security": cls.SECURITY_DB_PATH,
        }

    @classmethod
    def source_db_status(cls) -> dict:
        return {name: os.path.isfile(path) for name, path in cls.source_dbs().items()}
