import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID", "")
    BRAVE_API_KEY = os.getenv("BRAVE_API_KEY", "")
    SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")

    OUTPUT_DIR = os.getenv("LEAD_GEN_OUTPUT_DIR", "output")
    DEFAULT_MAX_LEADS = int(os.getenv("LEAD_GEN_DEFAULT_MAX_LEADS", "25"))
    DEFAULT_INDUSTRY = os.getenv(
        "LEAD_GEN_DEFAULT_INDUSTRY", "real estate agents"
    )
    DEFAULT_LOCATION = os.getenv(
        "LEAD_GEN_DEFAULT_LOCATION", "Austin, TX"
    )

    @classmethod
    def has_any_llm(cls) -> bool:
        return bool(cls.GROQ_API_KEY or cls.OPENAI_API_KEY)

    @classmethod
    def has_any_search(cls) -> bool:
        return bool(
            cls.GOOGLE_API_KEY or cls.BRAVE_API_KEY or cls.SERPAPI_API_KEY
        )
