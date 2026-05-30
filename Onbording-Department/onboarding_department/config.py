import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "onboarding@example.com")
    SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Client Onboarding Team")

    OUTREACH_DB_PATH = os.getenv("OUTREACH_DB_PATH", "output/outreach.db")

    OUTPUT_DIR = os.getenv("ONBOARDING_OUTPUT_DIR", "output")

    @classmethod
    def has_smtp(cls) -> bool:
        return bool(cls.SMTP_HOST and cls.SMTP_HOST != "localhost" and cls.SMTP_USER)

    @classmethod
    def outreach_db_exists(cls) -> bool:
        return os.path.isfile(cls.OUTREACH_DB_PATH)
