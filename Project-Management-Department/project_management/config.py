import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    ONBOARDING_DB_PATH = os.getenv("ONBOARDING_DB_PATH", "output/onboarding.db")

    OUTPUT_DIR = os.getenv("PM_OUTPUT_DIR", "output")

    SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "pm@example.com")
    SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Project Management Team")

    @classmethod
    def has_smtp(cls) -> bool:
        return bool(cls.SMTP_HOST and cls.SMTP_HOST != "localhost" and cls.SMTP_USER)

    @classmethod
    def onboarding_db_exists(cls) -> bool:
        return os.path.isfile(cls.ONBOARDING_DB_PATH)
