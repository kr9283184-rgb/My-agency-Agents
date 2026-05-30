import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

    OUTPUT_DIR = os.getenv("OUTREACH_OUTPUT_DIR", "output")
    DEFAULT_MAX_LEADS = int(os.getenv("OUTREACH_DEFAULT_MAX_LEADS", "10"))
    DEFAULT_INDUSTRY = os.getenv(
        "OUTREACH_DEFAULT_INDUSTRY", "real estate agents"
    )
    DEFAULT_LOCATION = os.getenv(
        "OUTREACH_DEFAULT_LOCATION", "Austin, TX"
    )

    SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "sales@example.com")
    SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Sales Team")

    CALDAV_URL = os.getenv("CALDAV_URL", "")
    CALDAV_USER = os.getenv("CALDAV_USER", "")
    CALDAV_PASSWORD = os.getenv("CALDAV_PASSWORD", "")

    RATE_LIMIT_EMAIL = int(os.getenv("RATE_LIMIT_EMAIL", "10"))
    RATE_LIMIT_WHATSAPP = int(os.getenv("RATE_LIMIT_WHATSAPP", "5"))
    RATE_LIMIT_LINKEDIN = int(os.getenv("RATE_LIMIT_LINKEDIN", "3"))
    RATE_LIMIT_FACEBOOK = int(os.getenv("RATE_LIMIT_FACEBOOK", "3"))
    RATE_LIMIT_TWITTER = int(os.getenv("RATE_LIMIT_TWITTER", "5"))

    @classmethod
    def has_ollama(cls) -> bool:
        return bool(cls.OLLAMA_BASE_URL)

    @classmethod
    def has_smtp(cls) -> bool:
        return bool(cls.SMTP_HOST and cls.SMTP_USER)
