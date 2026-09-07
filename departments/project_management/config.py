"""Project management configuration."""
import os

OUTPUT_DIR = os.getenv("PM_OUTPUT_DIR", "output/project_management")
DB_PATH = os.getenv("PM_DB_PATH", f"{OUTPUT_DIR}/department.db")
