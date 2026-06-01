import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    OUTPUT_DIR = os.getenv("WEBSITE_OUTPUT_DIR", "output")
    DB_PATH = os.getenv("WEBSITE_DB_PATH", os.path.join(OUTPUT_DIR, "website_development.db"))
    PM_DB_PATH = os.getenv("PM_DB_PATH", "../Project-Management-Department/output/pm.db")

    DEFAULT_PROJECT_TYPE = os.getenv("WEBSITE_DEFAULT_PROJECT_TYPE", "business_website")
    DEFAULT_PLATFORM = os.getenv("WEBSITE_DEFAULT_PLATFORM", "static")

    @classmethod
    def pm_db_exists(cls) -> bool:
        return os.path.isfile(cls.PM_DB_PATH)
