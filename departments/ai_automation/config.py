"""AI automation configuration."""
import os

OUTPUT_DIR = os.getenv("AUTOMATION_OUTPUT_DIR", "output/ai_automation")
DB_PATH = os.getenv("AUTOMATION_DB_PATH", f"{OUTPUT_DIR}/department.db")
